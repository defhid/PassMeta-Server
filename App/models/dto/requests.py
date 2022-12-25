__all__ = (
    'SignInDto',
    'SignUpDto',
    'UserPatchDto',
    'PassfilePostDto',
    'PassfilePatchDto',
    'PassfileDeleteDto',
    'HistoryPageParamsDto',
)

from pydantic import BaseModel, conint
from datetime import datetime, date


class SignInDto(BaseModel):
    login: str
    password: str

    class Config:
        extra = "forbid"


class SignUpDto(BaseModel):
    login: str
    password: str
    full_name: str

    class Config:
        extra = "forbid"


class UserPatchDto(BaseModel):
    full_name: str | None
    login: str | None
    password: str | None
    password_confirm: str | None

    class Config:
        extra = "forbid"


class PassfilePostDto(BaseModel):
    name: str
    color: str | None
    type_id: conint(ge=1, le=32767)
    created_on: datetime

    class Config:
        extra = "forbid"


class PassfilePatchDto(BaseModel):
    name: str
    color: str | None

    class Config:
        extra = "forbid"


class PassfileDeleteDto(BaseModel):
    check_password: str

    class Config:
        extra = "forbid"


class PageParamsDto(BaseModel):
    page_index: conint(ge=0)
    page_size: conint(ge=0, le=100)

    class Config:
        extra = "forbid"


class HistoryPageParamsDto(PageParamsDto):
    month: date
    kind: str = None
