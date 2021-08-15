from pydantic import BaseModel, constr
from typing import Optional
from App.models.db import *

__all__ = (
    'SignInPostData',
    'SignUpPostData',
    'UserSelfPatchData',
    'PassfilePostData',
)


class SignInPostData(BaseModel):
    login: constr(min_length=5, max_length=User.login.property.columns[0].type.length)
    password: constr(min_length=5, max_length=512)

    class Config:
        extra = "forbid"


class SignUpPostData(BaseModel):
    login: constr(min_length=5, max_length=User.login.property.columns[0].type.length)
    password: constr(min_length=5, max_length=512)
    first_name: constr(min_length=1, max_length=User.first_name.property.columns[0].type.length)
    last_name: constr(min_length=1, max_length=User.last_name.property.columns[0].type.length)

    class Config:
        extra = "forbid"


class UserSelfPatchData(BaseModel):
    login: Optional[constr(min_length=5, max_length=User.login.property.columns[0].type.length)]
    password: Optional[constr(min_length=5, max_length=512)]
    new_password: Optional[constr(min_length=5, max_length=512)]
    first_name: Optional[constr(min_length=1, max_length=User.first_name.property.columns[0].type.length)]
    last_name: Optional[constr(min_length=1, max_length=User.last_name.property.columns[0].type.length)]


class PassfilePostData(BaseModel):
    smth: constr(max_length=2_097_152)

    class Config:
        extra = "forbid"
