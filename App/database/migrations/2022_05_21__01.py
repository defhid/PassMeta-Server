from App.database.migrations.base import BaseMigration
from App.database.entities import *


class Migration(BaseMigration):
    def __init__(self):
        super().__init__('2022.05.21 01')

    async def apply(self):
        await self.db.execute("""
            CREATE SCHEMA IF NOT EXISTS public;

            DROP SCHEMA IF EXISTS history CASCADE;
            CREATE SCHEMA history;

            DROP TABLE IF EXISTS public.session;
        """)

        await self.create_migrations_table()
        await self.create_users_table()
        await self.create_passfiles_table()
        await self.create_histories_table()

    async def create_migrations_table(self):
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS public.migrations (
                name char(12) UNIQUE PRIMARY KEY,
                timestamp timestamp NOT NULL DEFAULT now()
            );
        """)

    async def create_users_table(self):
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS public.user (
                id serial UNIQUE PRIMARY KEY,
                login varchar(@LOGIN_LEN_MAX) NOT NULL UNIQUE,
                pwd char(@PASSWORD_LEN) NOT NULL,
                first_name varchar(@FIRST_NAME_LEN_MAX) NOT NULL,
                last_name varchar(@LAST_NAME_LEN_MAX) NOT NULL,
                is_active bool NOT NULL DEFAULT TRUE,

                CONSTRAINT login_min CHECK (length(login) >= @LOGIN_LEN_MIN),
                CONSTRAINT first_name_min CHECK (length(first_name) >= @FIRST_NAME_LEN_MIN),
                CONSTRAINT last_name_min CHECK (length(last_name) >= @LAST_NAME_LEN_MIN)
            );
            CREATE UNIQUE INDEX IF NOT EXISTS user_id_uix ON public.user(id);
            CREATE UNIQUE INDEX IF NOT EXISTS user_login_ix ON public.user(login);
        """, User.Constrains)

        await self.db.execute("""
            ALTER TABLE public.user RENAME TO users;
        """)

    async def create_passfiles_table(self):
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS public.passfile (
                id serial PRIMARY KEY,
                name varchar(@NAME_LEN_MAX) NOT NULL,
                color char(@COLOR_LEN) NULL,
                user_id int NOT NULL REFERENCES public.users(id),
                version int NOT NULL DEFAULT 0,
                created_on timestamp NOT NULL,
                info_changed_on timestamp NOT NULL,
                version_changed_on timestamp NOT NULL,

                CONSTRAINT name_min CHECK (length(name) >= @NAME_LEN_MIN),
                CONSTRAINT color_len CHECK (length(trim(color)) = @COLOR_LEN)
            );
            CREATE UNIQUE INDEX IF NOT EXISTS passfile_id_ix ON public.passfile(id);
            CREATE INDEX IF NOT EXISTS passfile_user_id_ix ON public.passfile(user_id);
        """, PassFile.Constrains)

        await self.db.execute("""
            ALTER TABLE public.passfile RENAME TO passfiles;
        """)

    async def create_histories_table(self):
        await self.db.execute("""
            CREATE TABLE history.histories (
                id bigserial PRIMARY KEY,
                kind_id smallint NOT NULL,
                user_id int NULL REFERENCES public.users(id)
                    ON DELETE SET NULL,
                affected_user_id int NULL REFERENCES public.users(id)
                    ON DELETE SET NULL,
                timestamp timestamp NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS history_user_id_ix ON history.histories(affected_user_id);
        """)

        await self.db.execute("""
            CREATE TABLE history.more_abstract (
                history_id bigint NOT NULL REFERENCES history.histories(id) ON DELETE RESTRICT,
                info varchar(@MORE_INFO_LEN_MAX) NOT NULL
            );
        """, History.Constrains)

        await self.db.execute("""
            DROP FUNCTION IF EXISTS add_history_more(bigint,text);

            CREATE FUNCTION add_history_more(p_history_id bigint, p_more text)
            RETURNS bigint
            LANGUAGE plpgsql AS $$
            DECLARE
                curr timestamp;
                more_table char(20);
                created BOOLEAN;
            BEGIN
                curr = date_trunc('month', now());
            
                more_table = 'history_more_' || to_char(curr, 'YYYY_MM');
                SELECT EXISTS(SELECT FROM information_schema.tables
                              WHERE table_schema = 'history' AND table_name = more_table) INTO created;
            
                IF NOT created THEN
                    EXECUTE('CREATE TABLE history.' || more_table || ' () INHERITS (history.more_abstract)');
                END IF;
            
                EXECUTE(format('INSERT INTO history.%I (history_id, info) VALUES (%s, %L)',
                                more_table, p_history_id, p_more));
            
                RETURN p_history_id;
            END; $$
        """)
