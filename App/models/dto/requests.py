__all__ = (
    'SignInDto',
    'SignUpDto',
    'UserPatchDto',
    'PassfileListParamsDto',
    'PassfilePostDto',
    'PassfilePatchDto',
    'HistoryPageParamsDto',
)

from pydantic import conint
from datetime import datetime, date

from App.models.dto.common import BaseDto


class SignInDto(BaseDto):
    login: str
    password: str

    class Config:
        extra = "forbid"


class SignUpDto(BaseDto):
    login: str
    password: str
    full_name: str

    class Config:
        extra = "forbid"


class UserPatchDto(BaseDto):
    full_name: str | None
    login: str | None
    password: str | None
    password_confirm: str | None

    class Config:
        extra = "forbid"


class PassfileListParamsDto(BaseDto):
    type_id: int | None

    class Config:
        extra = "forbid"


class PassfilePostDto(BaseDto):
    name: str
    color: str | None
    type_id: conint(ge=1, le=32767)
    created_on: datetime

    class Config:
        extra = "forbid"


class PassfilePatchDto(BaseDto):
    name: str
    color: str | None

    class Config:
        extra = "forbid"


class PageParamsDto(BaseDto):
    page_index: conint(ge=0)
    page_size: conint(ge=0, le=100)

    class Config:
        extra = "forbid"


class HistoryPageParamsDto(PageParamsDto):
    month: date
    kind: str | None = None
