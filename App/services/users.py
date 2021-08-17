from App.models.request import SignUpPostData, UserPatchData
from App.services.base import DbServiceBase
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
            Raises:
                ALREADY_USED_ERR: 'login',
                ...
        """
        login = data.login.strip()
        first_name = data.first_name.strip()
        last_name = data.last_name.strip()

        # TODO: many many checks

        if await self.db.query_first(User, select(User).where(User.login == login)):
            await self.history_writer.write(
                History.Kind.USER_REGISTER_FAILURE,
                None,
                more=f"login:{login}",
                request=request
            )
            raise Bad('login', ALREADY_USED_ERR)

        user = User(
            login=login,
            pwd=hashlib.sha512(data.password.encode('utf-8')).hexdigest(),
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )

        self.db.add(user)

        await self.history_writer.write(  # autocommit
            History.Kind.USER_REGISTER_SUCCESS,
            user,
            request=request
        )
        return user

    async def edit_user(self, user_id: int, data: UserPatchData, requester: User, request: Request) -> User:
        """ Auto-commit.
            Raises: ...
        """
        raise Bad(None, NOT_IMPLEMENTED)  # TODO: сделать
