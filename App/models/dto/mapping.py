__all__ = (
    'ResultMapping',
    'HistoryMapping',
    'PassFileMapping',
    'PassFileVersionMapping',
    'UserMapping',
)

from App.database import PassFile, User, History, PassFileVersion
from App.models.dto.responses import *
from App.models.okbad import Result
from App.translate import HISTORY_KINDS_TRANSLATE_PACK, OK_BAD_MESSAGES_TRANSLATE_PACK, get_package_text

from typing import Any
import ipaddress


class ResultMapping:
    @classmethod
    def to_dto(cls, res: Result, locale: str, data: Any = None) -> ResultDto:
        d = {
            'code': res.code.code,
            'msg': get_package_text(OK_BAD_MESSAGES_TRANSLATE_PACK,
                                    res.code, locale, res.code.name)
        }

        if data is not None:
            d['data'] = data

        if res.more:
            d['more'] = res.more.to_dict(locale)

        if res.what:
            if 'more' not in d:
                d['more'] = {}
            d['more']['what'] = res.what

        if res.sub:
            if 'more' not in d:
                d['more'] = {}
            d['more']['sub'] = [cls.to_dto(s, locale) for s in res.sub]

        return ResultDto.construct(**d)


class HistoryMapping:
    @classmethod
    def to_dto(cls, his: History, locale: str) -> HistoryDto:
        return HistoryDto.construct(
            id=his.id,
            kind=get_package_text(HISTORY_KINDS_TRANSLATE_PACK, his.kind_id, locale, his.kind_id),
            user_ip=str(ipaddress.ip_address(his.user_ip)),
            user_id=his.user_id,
            user_login=his.user_login,
            affected_user_id=his.affected_user_id,
            affected_user_login=his.affected_user_login,
            affected_passfile_id=his.affected_passfile_id,
            affected_passfile_name=his.affected_passfile_name,
            more=his.more.strip(),
            written_on=his.written_on.isoformat(),
        )


class PassFileMapping:
    @classmethod
    def to_dto(cls, pf: PassFile) -> PassfileDto:
        return PassfileDto.construct(
            id=pf.id,
            name=pf.name,
            color=pf.color,
            type_id=pf.type_id,
            user_id=pf.user_id,
            version=pf.version,
            created_on=pf.created_on.isoformat(),
            info_changed_on=pf.info_changed_on.isoformat(),
            version_changed_on=pf.version_changed_on.isoformat(),
        )


class PassFileVersionMapping:
    @classmethod
    def to_dict(cls, pfv: PassFileVersion) -> dict[str, Any]:
        return {
            'passfile_id': pfv.passfile_id,
            'version': pfv.version,
            'version_date': pfv.version_date.isoformat(),
        }


class UserMapping:
    @classmethod
    def to_dict(cls, usr: User) -> dict[str, Any]:
        return {
            'id': usr.id,
            'login': usr.login,
            'full_name': usr.full_name,
            'is_active': usr.is_active,
        }
