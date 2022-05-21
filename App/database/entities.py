from App.settings import PASSFILES_ENCODING
from App.translate import HISTORY_KINDS_TRANSLATE_PACK, get_package_text
from passql.models import DbEntity, register_entities
from datetime import datetime
from typing import Any, Dict, Optional

__all__ = (
    'User',
    'PassFile',
    'History',
)


class User(DbEntity):
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

    def to_dict(self, data: bytes = None) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'type_id': self.type_id,
            'user_id': self.user_id,
            'version': self.version,
            'created_on': self.created_on.isoformat(),
            'info_changed_on': self.info_changed_on.isoformat(),
            'version_changed_on': self.version_changed_on.isoformat(),
            'smth': None if data is None else data.decode(PASSFILES_ENCODING),
        }

    class Constrains:
        NAME_LEN_MIN = 1
        NAME_LEN_MAX = 100

        COLOR_LEN = 6

        class Raw:
            SMTH_MIN_LEN = 1


class History(DbEntity):
    id: int
    kind_id: int
    user_id: Optional[int]
    affected_user_id: Optional[int]
    timestamp: datetime

    # region +
    kind: Optional[str]
    more: Optional[str]
    user_login: Optional[str]
    affected_user_login: Optional[str]
    # endregion

    def to_dict(self, locale: str) -> Dict[str, Any]:
        return {
            'id': self.id,
            'kind': get_package_text(HISTORY_KINDS_TRANSLATE_PACK, self.kind_id, locale, self.kind_id),
            'user_login': self.user_login,
            'affected_user_login': self.affected_user_login,
            'more': self.more,
            'timestamp': self.timestamp.isoformat(),
        }

    class Constrains:
        MORE_INFO_LEN_MAX = 160


register_entities()
