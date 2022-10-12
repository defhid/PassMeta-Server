from passql.models import DbEntity, register_entities
from datetime import datetime
from typing import Optional

__all__ = (
    'User',
    'AuthKey',
    'PassFile',
    'PassFileVersion',
    'History',
)


class User(DbEntity):
    id: int
    login: str
    pwd: str
    first_name: str
    last_name: str
    is_active: bool

    class Constrains:
        LOGIN_LEN_MIN = 5
        LOGIN_LEN_MAX = 150

        PASSWORD_LEN = 128
        PASSWORD_RAW_LEN_MIN = 5
        PASSWORD_RAW_LEN_MAX = 128

        FIRST_NAME_LEN_MIN = 1
        FIRST_NAME_LEN_MAX = 120

        LAST_NAME_LEN_MIN = 1
        LAST_NAME_LEN_MAX = 120

    def __repr__(self) -> str:
        return f"<User #{self.id} {self.login}>"


class AuthKey(DbEntity):
    id: int
    user_id: int
    secret_key: str

    def __repr__(self) -> str:
        return f"<AuthKey #{self.id} {self.secret_key}>"


class PassFile(DbEntity):
    id: int
    name: str
    color: Optional[str]  # hex
    type_id: int
    user_id: int
    version: int
    created_on: datetime
    info_changed_on: datetime
    version_changed_on: datetime

    class Constrains:
        NAME_LEN_MIN = 1
        NAME_LEN_MAX = 100

        COLOR_LEN = 6

        SMTH_RAW_LEN_MIN = 1

    def __repr__(self) -> str:
        return f"<PassFile #{self.id} {self.name} v{self.version}>"


class PassFileVersion(DbEntity):
    passfile_id: Optional[int]
    version: int
    version_date: datetime

    # region +
    user_id: Optional[int]
    # endregion

    def __repr__(self) -> str:
        return f"<PassFileVersion pf{self.passfile_id} v{self.version} {self.version_date}>"


class History(DbEntity):
    id: int
    kind_id: int
    user_ip: int
    user_id: Optional[int]
    affected_user_id: Optional[int]
    affected_passfile_id: Optional[int]
    more: str
    written_on: datetime

    # region +
    kind: Optional[str]
    user_login: Optional[str]
    affected_user_login: Optional[str]
    affected_passfile_name: Optional[str]
    # endregion

    class Constrains:
        MORE_LEN = 10

    def __repr__(self) -> str:
        return f"<History #{self.id} {self.kind_id} {self.more}>"


register_entities()
