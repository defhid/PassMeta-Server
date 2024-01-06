__all__ = (
    'ResultDto',
    'FullResultDto',

    'PageDto',
    'UserDto',
    'AppInfoDto',

    'PassfileDto',
    'PassfileListDto',
    'PassfileVersionDto',
    'PassfileVersionListDto',

    'HistoryDto',
    'HistoryPageDto',
    'HistoryKindDto',
    'HistoryKindListDto',

    'ERROR_RESPONSES',
)

from datetime import datetime

from App.models.dto.common import BaseDto


class ResultDto(BaseDto):
    code: int
    msg: str


class FullResultDto(ResultDto):
    more: list[str] | None


class PageDto(BaseDto):
    list: list[dict]
    total: int
    page_size: int
    page_index: int


class UserDto(BaseDto):
    id: int
    login: str
    full_name: str
    is_active: bool


class AppInfoDto(BaseDto):
    app_id: str
    app_version: str
    user: UserDto


class PassfileDto(BaseDto):
    id: int
    name: str
    color: str | None
    type_id: int
    user_id: int
    version: int
    created_on: datetime
    info_changed_on: datetime
    version_changed_on: datetime

class PassfileListDto(BaseDto):
    list: list[PassfileDto]


class PassfileVersionDto(BaseDto):
    passfile_id: int
    version: int
    version_date: datetime

class PassfileVersionListDto(BaseDto):
    list: list[PassfileVersionDto]


class HistoryKindDto(BaseDto):
    id: int
    name: str

class HistoryKindListDto(BaseDto):
    list: list[HistoryKindDto]


class HistoryDto(BaseDto):
    id: int
    kind: str
    user_ip: str
    user_id: int
    user_login: str | None
    affected_user_id: int | None
    affected_user_login: str | None
    affected_passfile_id: int | None
    affected_passfile_name: str | None
    more: str | None
    written_on: datetime


class HistoryPageDto(PageDto):
    list: list[HistoryDto]


ERROR_RESPONSES = {
    400: { 'model': FullResultDto },
    401: { 'model': FullResultDto },
    403: { 'model': FullResultDto },
    404: { 'model': FullResultDto },
    422: { 'model': FullResultDto },
    500: { 'model': FullResultDto },
}
