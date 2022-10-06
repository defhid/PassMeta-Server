from App.database.migrations.base import BaseMigration
from App.database.entities import *


class Migration(BaseMigration):
    def __init__(self):
        super().__init__('2022.05.21 01')

    async def apply(self):
        await self.db.execute("""
            DROP SCHEMA IF EXISTS public CASCADE;
            CREATE SCHEMA public;

            DROP SCHEMA IF EXISTS history CASCADE;
            CREATE SCHEMA history;
        """)

        await self.create_migrations_table()
        await self.create_users_table()
        await self.create_auth_keys_table()
        await self.create_passfiles_table()
        await self.create_passfile_versions_table()
        await self.create_histories_table()

    async def create_migrations_table(self):
        await self.db.execute("""
            CREATE TABLE public.migrations (
                name char(12) UNIQUE PRIMARY KEY,
                timestamp timestamp NOT NULL DEFAULT now()
            );
        """)

    async def create_users_table(self):
        await self.db.execute("""
            CREATE TABLE public.users (
                id bigserial UNIQUE PRIMARY KEY,
                login varchar(@LOGIN_LEN_MAX) NOT NULL UNIQUE,
                pwd char(@PASSWORD_LEN) NOT NULL,
                first_name varchar(@FIRST_NAME_LEN_MAX) NOT NULL,
                last_name varchar(@LAST_NAME_LEN_MAX) NOT NULL,
                is_active bool NOT NULL DEFAULT TRUE,

                CONSTRAINT login_min CHECK (length(login) >= @LOGIN_LEN_MIN),
                CONSTRAINT first_name_min CHECK (length(first_name) >= @FIRST_NAME_LEN_MIN),
                CONSTRAINT last_name_min CHECK (length(last_name) >= @LAST_NAME_LEN_MIN)
            );
            CREATE UNIQUE INDEX users_id_uix ON public.users(id);
            CREATE UNIQUE INDEX users_login_ix ON public.users(login);
        """, User.Constrains)

    async def create_auth_keys_table(self):
        await self.db.execute("""
            CREATE TABLE public.auth_keys (
                id serial PRIMARY KEY,
                user_id int NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
                secret_key uuid NOT NULL
            );
            CREATE UNIQUE INDEX auth_keys_user_id_uix ON public.auth_keys(user_id);
        """)

    async def create_passfiles_table(self):
        await self.db.execute("""
            CREATE TABLE public.passfiles (
                id bigserial PRIMARY KEY,
                name varchar(@NAME_LEN_MAX) NOT NULL,
                color char(@COLOR_LEN) NULL,
                type_id smallint NOT NULL,
                user_id bigint NOT NULL REFERENCES public.users(id),
                version int NOT NULL DEFAULT 0,
                created_on timestamp NOT NULL,
                info_changed_on timestamp NOT NULL,
                version_changed_on timestamp NOT NULL,

                CONSTRAINT name_min CHECK (length(name) >= @NAME_LEN_MIN),
                CONSTRAINT color_len CHECK (length(trim(color)) = @COLOR_LEN)
            );
            CREATE UNIQUE INDEX passfiles_id_ix ON public.passfiles(id);
            CREATE INDEX passfiles_user_id_ix ON public.passfiles(user_id);
        """, PassFile.Constrains)

    async def create_passfile_versions_table(self):
        await self.db.execute("""
            CREATE TABLE public.passfile_versions (
                passfile_id bigint NOT NULL REFERENCES public.passfiles(id) ON DELETE RESTRICT,
                version int NOT NULL,
                version_date timestamp NOT NULL
            );
            CREATE INDEX passfile_versions_passfile_id_ix
            ON public.passfile_versions(passfile_id);
            CREATE UNIQUE INDEX passfile_versions_passfile_id_version_uix
            ON public.passfile_versions(passfile_id, version);
        """)

    async def create_histories_table(self):
        await self.db.execute("""
            CREATE TABLE history.histories_abstract (
                id bigserial PRIMARY KEY,
                kind_id smallint NOT NULL,
                user_id bigint NULL,
                affected_user_id bigint NULL,
                affected_passfile_id bigint NULL,
                more char(16) NOT NULL,
                written_on timestamp NOT NULL
            );

            CREATE INDEX histories_abstract_affected_user_id_ix ON history.histories_abstract(affected_user_id);

            DROP FUNCTION IF EXISTS history.add_history(smallint, bigint, bigint, bigint, char(@MORE_LEN));

            CREATE FUNCTION history.add_history(
                p_kind_id smallint,
                p_user_id bigint,
                p_affected_user_id bigint,
                p_affected_passfile_id bigint,
                p_more char(@MORE_LEN)
            )
            RETURNS void
            LANGUAGE plpgsql AS $$
            DECLARE
                history_table char(17);
                created BOOLEAN;
            BEGIN
                history_table = 'histories_' || to_char(now(), 'YYYY_MM');

                EXECUTE(format('INSERT INTO history.%I (kind_id, user_id, affected_user_id, affected_passfile_id, more, written_on) VALUES (%L, %L, %L, %L, %L, now())',
                                history_table, p_kind_id, p_user_id, p_affected_user_id, p_affected_passfile_id, coalesce(p_more, '')));
            EXCEPTION WHEN OTHERS
            THEN
                SELECT EXISTS(SELECT FROM information_schema.tables
                              WHERE table_schema = 'history' AND table_name = history_table) INTO created;

                IF NOT created THEN
                    RAISE NOTICE 'Creating a history partition %', history_table;

                    EXECUTE(format('CREATE TABLE IF NOT EXISTS history.%I (LIKE history.histories_abstract INCLUDING INDEXES);' ||
                                   'INSERT INTO history.%I (kind_id, user_id, affected_user_id, affected_passfile_id, more, written_on)' ||
                                   'VALUES (%L, %L, %L, %L, %L, now());',
                                    history_table, history_table, p_kind_id, p_user_id, p_affected_user_id, p_affected_passfile_id, coalesce(p_more, '')));
                ELSE
                    RAISE EXCEPTION 'ERROR CODE: %. MESSAGE TEXT: %', SQLSTATE, SQLERRM;
                END IF;
            END; $$;
       """, History.Constrains)
