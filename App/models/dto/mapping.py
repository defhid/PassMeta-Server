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
from App.translate import HISTORY_KINDS_TRANSLATE_PACK, OK_BAD_TRANSLATE_PACK, get_package_text

import ipaddress


class ResultMapping:
    @classmethod
    def to_dto(cls, res: Result, locale: str) -> FullResultDto:
        return FullResultDto.model_construct(
            code=res.code.code,
            msg=get_package_text(OK_BAD_TRANSLATE_PACK, res.code, locale, res.code.name),
            more=list(map(lambda x: x.to_message(locale), res.more)) if res.more else None,
        )


class HistoryMapping:
    @classmethod
    def to_dto(cls, his: History, locale: str) -> HistoryDto:
        return HistoryDto.model_construct(
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
            written_on=his.written_on,
        )


class PassFileMapping:
    @classmethod
    def to_dto(cls, pf: PassFile) -> PassfileDto:
        return PassfileDto.model_construct(
            id=pf.id,
            name=pf.name,
            color=pf.color,
            type_id=pf.type_id,
            user_id=pf.user_id,
            version=pf.version,
            created_on=pf.created_on,
            info_changed_on=pf.info_changed_on,
            version_changed_on=pf.version_changed_on,
        )


class PassFileVersionMapping:
    @classmethod
    def to_dto(cls, pfv: PassFileVersion) -> PassfileVersionDto:
        return PassfileVersionDto.model_construct(
            passfile_id=pfv.passfile_id,
            version=pfv.version,
            version_date=pfv.version_date,
        )


class UserMapping:
    @classmethod
    def to_dto(cls, usr: User) -> UserDto:
        return UserDto.model_construct(
            id=usr.id,
            login=usr.login,
            full_name=usr.full_name,
            is_active=usr.is_active,
        )
