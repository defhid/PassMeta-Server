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
    """ User entity.
    """

    """ user identifier """
    id: int

    """ login for identification """
    login: str

    """ password hash for authentication """
    pwd: str

    """ full name """
    full_name: str

    """ not blocked """
    is_active: bool

    class Constrains:
        LOGIN_LEN_MIN = 5
        LOGIN_LEN_MAX = 80

        PASSWORD_LEN = 128
        PASSWORD_RAW_LEN_MIN = 5
        PASSWORD_RAW_LEN_MAX = 128

        FULL_NAME_LEN_MIN = 1
        FULL_NAME_LEN_MAX = 120

    def __repr__(self) -> str:
        return f"<User id={self.id} login={self.login} name={self.full_name}>"


class AuthKey(DbEntity):
    """ Authentication key entity.
    """

    """ user identifier """
    user_id: int

    """ user authentication key """
    secret_key: str

    def __repr__(self) -> str:
        return f"<AuthKey user_id={self.user_id} key={self.secret_key}>"


class PassFile(DbEntity):
    """ Passfile entity.
    """

    """ passfile identifier """
    id: int

    """ passfile type identifier """
    type_id: int

    """ passfile owner identifier """
    user_id: int

    """ passfile name """
    name: str

    """ color in hex format """
    color: Optional[str]

    """ data version """
    version: int

    """ timestamp of creation """
    created_on: datetime

    """ timestamp of last information change """
    info_changed_on: datetime

    """ timestamp of last data change """
    version_changed_on: datetime

    class Constrains:
        NAME_LEN_MIN = 1
        NAME_LEN_MAX = 100

        COLOR_LEN = 6

        SMTH_RAW_LEN_MIN = 1

    def __repr__(self) -> str:
        return f"PassFile id={self.id} name={self.name} v{self.version}>"


class PassFileVersion(DbEntity):
    """ Passfile data version entity.
    """

    """ passfile identifier """
    passfile_id: Optional[int]

    """ data version """
    version: int

    """ data version timestamp """
    version_date: datetime

    # region JOIN

    """ user identifier of the passfile owner """
    user_id: Optional[int]

    # endregion

    def __repr__(self) -> str:
        return f"<PassFileVersion pf={self.passfile_id} v{self.version} {self.version_date}>"


class History(DbEntity):
    """ History record entity.
    """

    """ history record identifier """
    id: int

    """ history kind identifier """
    kind_id: int

    """ user-subject IP address """
    user_ip: Optional[int]

    """ user-subject identifier """
    user_id: Optional[int]

    """ user-object identifier """
    affected_user_id: Optional[int]

    """ passfile-object identifier """
    affected_passfile_id: Optional[int]

    """ additional short information """
    more: str

    """ timestamp """
    written_on: datetime

    # region JOIN

    """ history kind name """
    kind: Optional[str]

    """ user-subject login """
    user_login: Optional[str]

    """ user-object login """
    affected_user_login: Optional[str]

    """ passfile-object name """
    affected_passfile_name: Optional[str]

    # endregion

    class Constrains:
        MORE_LEN = 10

    def __repr__(self) -> str:
        return f"<History kind={self.kind_id} written={self.written_on} more={self.more}>"


register_entities()
