from typing import Optional, List
from pydantic import BaseModel, constr, conint
from datetime import datetime

__all__ = (
    'SignInDto',
    'SignUpDto',
    'UserPatchDto',
    'PassfilePostDto',
    'PassfileInfoDto',
    'PassfileVersionDto',
    'PassfileDeleteDto',
    'HistoryPageParamsDto',

    'PageDto',
    'UserDto',
    'AppInfoDto',
    'PassFileDto',
    'PassFileFullDto',
    'PassFileVersionDto',
    'HistoryKindDto',
    'HistoryDto',
    'HistoryPageDto'
)


# region Request

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
    full_name: Optional[str]
    login: Optional[str]
    password: Optional[str]
    password_confirm: Optional[str]

    class Config:
        extra = "forbid"


class PassfilePostDto(BaseModel):
    name: str
    color: Optional[str]
    type_id: conint(ge=1, le=32767)
    created_on: datetime
    smth: constr(min_length=1, max_length=10_485_760)

    class Config:
        extra = "forbid"


class PassfileInfoDto(BaseModel):
    name: str
    color: Optional[str]

    class Config:
        extra = "forbid"


class PassfileVersionDto(BaseModel):
    smth: constr(min_length=1, max_length=2_097_152)

    class Config:
        extra = "forbid"


class PassfileDeleteDto(BaseModel):
    check_password: str

    class Config:
        extra = "forbid"


class PageParamsDto(BaseModel):
    offset: conint(ge=0)
    limit: conint(ge=0, le=100)

    class Config:
        extra = "forbid"


class HistoryPageParamsDto(PageParamsDto):
    month: datetime
    kind: str = None

# endregion


# region Response

class PageDto(BaseModel):
    list: List
    total: int
    offset: int
    limit: int


class UserDto(BaseModel):
    id: int
    login: str
    full_name: str
    is_active: bool


class AppInfoDto(BaseModel):
    app_id: str
    app_version: str
    user: UserDto


class PassFileDto(BaseModel):
    id: int
    name: str
    color: Optional[str]
    user_id: int
    version: int
    created_on: datetime
    info_changed_on: datetime
    version_changed_on: datetime


class PassFileFullDto(PassFileDto):
    smth: str


class PassFileVersionDto(BaseModel):
    passfile_id: int
    version: int
    version_date: datetime


class HistoryKindDto(BaseModel):
    id: int
    name: str


class HistoryDto(BaseModel):
    id: int
    kind: str
    user_login: Optional[str]
    affected_user_login: Optional[str]
    more: Optional[str]
    timestamp: datetime


class HistoryPageDto(PageDto):
    list: List[HistoryDto]


# endregion
