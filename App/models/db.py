from App.models.extra import *
from App.utils.db import MakeSql
from App.utils.logging import Logger
from App.settings import CHECK_DATABASE_ON_SATRTUP
from passql.models import DbEntity, register_entities
from passql import DbConnection
from datetime import datetime
from typing import Any, Dict, Optional

__all__ = (
    'User',
    'Session',
    'PassFile',
    'History',
    'check_entities',
)


class User(DbEntity):
    # region SQL

    TABLE = """
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
    """

    class Constrains:
        LOGIN_LEN_MIN = 5
        LOGIN_LEN_MAX = 150

        PASSWORD_LEN = 128

        FIRST_NAME_LEN_MIN = 1
        FIRST_NAME_LEN_MAX = 120

        LAST_NAME_LEN_MIN = 1
        LAST_NAME_LEN_MAX = 120

        class Raw:
            PASSWORD_LEN_MIN = 5
            PASSWORD_LEN_MAX = 128

    # endregion

    id: int
    login: str
    pwd: str
    first_name: str
    last_name: str
    is_active: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'login': self.login,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
        }


class Session(DbEntity):
    # region SQL

    TABLE = """
    CREATE TABLE IF NOT EXISTS public.session (
        id char(36) UNIQUE PRIMARY KEY DEFAULT uuid_in(overlay(
            overlay(md5(random()::text || ':' || clock_timestamp()::text) placing '4' from 13) 
            placing to_hex(floor(random()*(11-8+1) + 8)::int)::text from 17)::cstring),
        user_id int NOT NULL REFERENCES public.user(id),
        created_on timestamp NOT NULL DEFAULT now()
    );
    CREATE UNIQUE INDEX IF NOT EXISTS session_id_ix ON public.session(id);
    """

    _SELECT_USER = MakeSql("""SELECT * FROM "user" WHERE id = @user_id""")

    # endregion

    id: str
    user_id: int
    created_on: datetime

    async def get_user(self, db: DbConnection) -> 'User':
        return await db.query_first(User, self._SELECT_USER, self)


class PassFile(DbEntity):
    # region SQL

    TABLE = """
    CREATE TABLE IF NOT EXISTS public.passfile (
        id serial PRIMARY KEY,
        name varchar(@NAME_LEN_MAX) NOT NULL,
        color char(@COLOR_LEN) NULL,
        user_id int NOT NULL REFERENCES public.user(id),
        check_key char(@CHECK_KEY_LEN) NOT NULL,
        created_on timestamp NOT NULL DEFAULT now(),
        changed_on timestamp NOT NULL,
        version int NOT NULL DEFAULT 0,
        archived_on timestamp NULL,
        
        CONSTRAINT name_min CHECK (length(name) >= @NAME_LEN_MIN),
        CONSTRAINT color_len CHECK (length(trim(color)) = @COLOR_LEN),
        CONSTRAINT check_key_len CHECK (length(trim(check_key)) = @CHECK_KEY_LEN)
    );
    CREATE UNIQUE INDEX IF NOT EXISTS passfile_id_ix ON public.passfile(id);
    CREATE INDEX IF NOT EXISTS passfile_user_id_ix ON public.passfile(user_id);
    """

    class Constrains:
        NAME_LEN_MIN = 1
        NAME_LEN_MAX = 100

        COLOR_LEN = 6

        CHECK_KEY_LEN = 128

        class Raw:
            SMTH_MIN_LEN = 1

    # endregion

    id: int
    name: str
    color: Optional[str]  # hex
    user_id: int
    check_key: str
    created_on: datetime
    changed_on: datetime  # info changed
    version: int  # 'smth' data changed
    archived_on: datetime

    @property
    def is_archived(self) -> bool:
        return self.archived_on is not None

    def to_dict(self, data: bytes = None) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'check_key': self.check_key,
            'created_on': self.created_on.isoformat(),
            'changed_on': self.changed_on.isoformat(),
            'version': self.version,
            'is_archived': self.is_archived,
            'archived_on': self.archived_on.isoformat() if self.archived_on is not None else None,
            'smth': None if data is None else data.decode('utf-8'),
        }


class History(DbEntity):
    # region SQL

    SCHEMA = """
    CREATE SCHEMA IF NOT EXISTS history;
    """

    TABLE = """
    CREATE TABLE IF NOT EXISTS history.history (
        id bigserial PRIMARY KEY,
        kind_id smallint NOT NULL,
        user_id int NULL REFERENCES public.user(id)
            ON DELETE SET NULL,
        affected_user_id int NULL REFERENCES public.user(id)
            ON DELETE SET NULL,
        timestamp timestamp NOT NULL DEFAULT now()
    );
    CREATE INDEX IF NOT EXISTS history_user_id_ix ON history.history(affected_user_id);
    """

    FUNCTION = """
    CREATE OR REPLACE FUNCTION add_history_more(history_id bigint, more text)
    RETURNS bigint
    LANGUAGE plpgsql AS $$
    DECLARE 
        more_table char(20);
        created BOOLEAN;
    BEGIN
        more_table = 'history_more_' || to_char(now(), 'YYYY_MM');
        SELECT EXISTS(SELECT FROM information_schema.tables 
                      WHERE table_schema = 'history' AND table_name = more_table INTO created);

        IF NOT created THEN
            EXECUTE('CREATE TABLE history.' || more_table || ' (
                history_id bigint REFERENCES history.history(id) ON DELETE CASCADE,
                info varchar(@MORE_INFO_LEN_MAX) NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ' || more_table || '_ix ON history.' || more_table || '(history_id);');
        END IF;

        EXECUTE(format('INSERT INTO history.%I (history_id, info) VALUES (%s, %L)', more_table, history_id, more));
        RETURN history_id;
    END; $$
    """

    class Constrains:
        MORE_INFO_LEN_MAX = 160

    # endregion

    id: int
    kind_id: int
    user_id: Optional[int]
    affected_user_id: Optional[int]
    timestamp: datetime

    # region +
    more: Optional[str]
    user_login: Optional[str]
    affected_user_login: Optional[str]
    # endregion

    Kind = HistoryKinds.init()

    def to_dict(self, lang: str) -> Dict[str, Any]:
        return {
            'id': self.id,
            'kind_id': self.kind_id,
            'kind': self.Kind.get_by_id(self.kind_id).name_loc[lang],
            'user_login': self.user_login,
            'affected_user_login': self.affected_user_login,
            'more': self.more,
            'timestamp': self.timestamp.isoformat(),
        }


register_entities()


async def check_entities(connection: DbConnection):
    check_list = [
        (User.TABLE, User.Constrains),
        (Session.TABLE, None),
        (PassFile.TABLE, PassFile.Constrains),
        (History.SCHEMA, None),
        (History.TABLE, None),
        (History.FUNCTION, History.Constrains),
    ]

    if CHECK_DATABASE_ON_SATRTUP:
        for check in check_list:
            await connection.execute(check[0], check[1])

        Logger(__file__).info("DATABASE SUCCESSFULLY CHECKED")
