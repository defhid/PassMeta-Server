__all__ = (
    'ResultDto',
    'FullResultDto',

    'PageDto',
    'UserDto',
    'AppInfoDto',
    'PassfileDto',
    'PassfileVersionDto',
    'HistoryKindDto',
    'HistoryDto',
    'HistoryPageDto',

    'ERROR_RESPONSES',
)

from typing import Any
from pydantic import BaseModel
from datetime import datetime


class MoreDto(BaseModel):
    what: str | None
    text: str | None
    info: dict | None
    sub: list[dict] | None  # List of ResultDto


class ResultDto(BaseModel):
    code: int
    msg: str


class BadResultDto(ResultDto):
    more: MoreDto | None


class FullResultDto(ResultDto):
    more: MoreDto | None
    data: Any


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


class PassfileVersionDto(BaseModel):
    passfile_id: int
    version: int
    version_date: datetime


class HistoryKindDto(BaseModel):
    id: int
    name: str


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
    422: {
        'model': BadResultDto,
        'description': "Error Response. All supported status codes: 400, 401, 403, 404, 422, 500, 501.",
    },
}