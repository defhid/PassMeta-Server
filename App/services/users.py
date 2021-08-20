from App.services.base import DbServiceBase
from App.models.request import SignUpPostData, UserPatchData
from App.models.db import User, History
from App.special import *

from sqlalchemy import select
from starlette.requests import Request

import hashlib

__all__ = (
    'UserService',
)


class UserService(DbServiceBase):
    __slots__ = ()

    async def create_user(self, data: SignUpPostData, request: Request) -> User:
        """ Auto-commit.
        """
        user = User(
            login=data.login,
            first_name=data.first_name,
            last_name=data.last_name,
            is_active=True,
        )

        self._validate_and_prepare_user_to_save(user, data.password)

        if await self.db.query_first(User, select(User).where(User.login == user.login)):
            await self.history_writer.write(
                History.Kind.USER_REGISTER_FAILURE,
                None,
                more=f"login:{user.login}",
                request=request
            )
            raise Bad('login', ALREADY_USED_ERR)

        self.db.add(user)

        await self.history_writer.write(  # autocommit
            History.Kind.USER_REGISTER_SUCCESS,
            user,
            request=request
        )
        return user

    async def edit_user(self, user_id: int, data: UserPatchData, editor: User, request: Request) -> User:
        """ Auto-commit.
        """
        user = await self.db.query_first(User, select(User).where(User.id == user_id))

        if user.id != editor.id:
            raise Bad(None, NOT_IMPLEMENTED_ERR)

        if data.password_confirm is None:
            await self.history_writer.write(  # autocommit
                History.Kind.USER_EDIT_FAILURE,
                user,
                f"passconf_miss,editor:{editor.id}",
                request=request
            )
            raise Bad('password_confirm', VAL_MISSED_ERR)

        check_pwd = hashlib.sha512(data.password_confirm.encode('utf-8')).hexdigest()
        if check_pwd != user.pwd:
            await self.history_writer.write(  # autocommit
                History.Kind.USER_EDIT_FAILURE,
                user,
                f"passconf_wrong,editor:{editor.id}",
                request=request
            )
            raise Bad('password_confirm', WRONG_VAL_ERR)

        fields = ('login', 'first_name', 'last_name')
        for f in fields:
            if getattr(data, f) is not None:
                setattr(user, f, getattr(data, f))

        self._validate_and_prepare_user_to_save(user, data.password)

        await self.history_writer.write(  # autocommit
            History.Kind.USER_EDIT_SUCCESS,
            user,
            f"editor:{editor.id}",
            request=request
        )

        await self.db.refresh(user)
        return user

    def _validate_and_prepare_user_to_save(self, user: User, password: Optional[str]):
        r = self.Restrictions

        user.login = user.login.strip()

        if len(user.login) < r.LOGIN_LEN[0]:
            raise Bad('login', TOO_SHORT_ERR, MORE.min_allowed(r.LOGIN_LEN[0]))
        if len(user.login) > r.LOGIN_LEN[1]:
            raise Bad('login', TOO_LONG_ERR, MORE.max_allowed(r.LOGIN_LEN[1]))

        user.first_name = user.first_name.strip()

        if len(user.first_name) < r.FIRST_NAME_LEN[0]:
            raise Bad('first_name', TOO_SHORT_ERR, MORE.min_allowed(r.FIRST_NAME_LEN[0]))
        if len(user.first_name) > r.FIRST_NAME_LEN[1]:
            raise Bad('first_name', TOO_LONG_ERR, MORE.max_allowed(r.FIRST_NAME_LEN[1]))

        user.last_name = user.last_name.strip()

        if len(user.last_name) < r.LAST_NAME_LEN[0]:
            raise Bad('last_name', TOO_SHORT_ERR, MORE.min_allowed(r.LAST_NAME_LEN[0]))
        if len(user.last_name) > r.LAST_NAME_LEN[1]:
            raise Bad('last_name', TOO_LONG_ERR, MORE.max_allowed(r.LAST_NAME_LEN[1]))

        if password is not None:
            if len(password) < r.PASSWORD_LEN[0]:
                raise Bad('password', TOO_SHORT_ERR, MORE.min_allowed(r.PASSWORD_LEN[0]))
            if len(password) > r.PASSWORD_LEN[1]:
                raise Bad('password', TOO_LONG_ERR, MORE.max_allowed(r.PASSWORD_LEN[1]))

            user.pwd = hashlib.sha512(password.encode('utf-8')).hexdigest()

        elif not user.id:
            raise Bad('password', VAL_MISSED_ERR)

    class Restrictions:
        LOGIN_LEN = (5, User.login.property.columns[0].type.length)

        FIRST_NAME_LEN = (1, User.first_name.property.columns[0].type.length)

        LAST_NAME_LEN = (1, User.last_name.property.columns[0].type.length)

        PASSWORD_LEN = (5, 128)
