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

from pydantic import BaseModel, TypeAdapter
from datetime import datetime


class ResultDto(BaseModel):
    code: int
    msg: str


class FullResultDto(ResultDto):
    more: list[str] | None


class PageDto(BaseModel):
    list: list[dict]
    total: int
    page_size: int
    page_index: int


class UserDto(BaseModel):
    id: int
    login: str
    full_name: str
    is_active: bool


class AppInfoDto(BaseModel):
    app_id: str
    app_version: str
    user: UserDto


class PassfileDto(BaseModel):
    id: int
    name: str
    color: str | None
    type_id: int
    user_id: int
    version: int
    created_on: datetime
    info_changed_on: datetime
    version_changed_on: datetime

class PassfileListDto(BaseModel):
    list: list[PassfileDto]


class PassfileVersionDto(BaseModel):
    passfile_id: int
    version: int
    version_date: datetime

class PassfileVersionListDto(BaseModel):
    list: list[PassfileVersionDto]


class HistoryKindDto(BaseModel):
    id: int
    name: str

class HistoryKindListDto(BaseModel):
    list: list[HistoryKindDto]


class HistoryDto(BaseModel):
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
    400: {
        'model': ResultDto,
        'description': "Error Response. All supported status codes: 400, 401, 403, 404, 500.",
    },
}
