from App.database import PassFile, User, History, PassFileVersion
from App.settings import PASSFILES_ENCODING
from App.translate import HISTORY_KINDS_TRANSLATE_PACK, get_package_text

from typing import Dict, Any
import ipaddress

__all__ = (
    'HistoryMapping',
    'PassFileMapping',
    'PassFileVersionMapping',
    'UserMapping',
)


class HistoryMapping:
    @classmethod
    def to_dict(cls, his: History, locale: str) -> Dict[str, Any]:
        return {
            'id': his.id,
            'kind': get_package_text(HISTORY_KINDS_TRANSLATE_PACK, his.kind_id, locale, his.kind_id),
            'user_ip': str(ipaddress.ip_address(his.user_ip)),
            'user_id': his.user_id,
            'user_login': his.user_login,
            'affected_user_id': his.affected_user_id,
            'affected_user_login': his.affected_user_login,
            'affected_passfile_id': his.affected_passfile_id,
            'affected_passfile_name': his.affected_passfile_name,
            'more': his.more.strip(),
            'timestamp': his.written_on.isoformat(),
        }


class PassFileMapping:
    @classmethod
    def to_dict(cls, pf: PassFile, smth: bytes = None) -> Dict[str, Any]:
        return {
            'id': pf.id,
            'name': pf.name,
            'color': pf.color,
            'type_id': pf.type_id,
            'user_id': pf.user_id,
            'version': pf.version,
            'created_on': pf.created_on.isoformat(),
            'info_changed_on': pf.info_changed_on.isoformat(),
            'version_changed_on': pf.version_changed_on.isoformat(),
            'smth': None if smth is None else smth.decode(PASSFILES_ENCODING),
        }


class PassFileVersionMapping:
    @classmethod
    def to_dict(cls, pfv: PassFileVersion) -> Dict[str, Any]:
        return {
            'passfile_id': pfv.passfile_id,
            'version': pfv.version,
            'version_date': pfv.version_date.isoformat(),
        }


class UserMapping:
    @classmethod
    def to_dict(cls, usr: User) -> Dict[str, Any]:
        return {
            'id': usr.id,
            'login': usr.login,
            'first_name': usr.first_name,
            'last_name': usr.last_name,
            'is_active': usr.is_active,
        }
