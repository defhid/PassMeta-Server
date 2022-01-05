from pydantic import BaseModel, constr
from typing import Optional
import datetime

__all__ = (
    'SignInPostData',
    'SignUpPostData',
    'UserPatchData',
    'PassfilePostData',
    'PassfileInfoPatchData',
    'PassfileSmthPatchData',
    'PassfileDeleteData',
)


class SignInPostData(BaseModel):
    login: str
    password: str

    class Config:
        extra = "forbid"


class SignUpPostData(BaseModel):
    login: str
    password: str
    first_name: str
    last_name: str

    class Config:
        extra = "forbid"


class UserPatchData(BaseModel):
    login: Optional[str]
    password: Optional[str]
    password_confirm: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]

    class Config:
        extra = "forbid"


class PassfilePostData(BaseModel):
    name: str
    color: Optional[str]
    created_on: datetime.datetime
    smth: constr(min_length=1, max_length=10_485_760)

    class Config:
        extra = "forbid"


class PassfileInfoPatchData(BaseModel):
    name: str
    color: Optional[str]

    class Config:
        extra = "forbid"


class PassfileSmthPatchData(BaseModel):
    smth: constr(min_length=1, max_length=2_097_152)

    class Config:
        extra = "forbid"


class PassfileDeleteData(BaseModel):
    check_password: str

    class Config:
        extra = "forbid"
