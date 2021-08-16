from App.models.request import SignUpPostData, UserSelfPatchData
from App.utils.db import AsyncDbSession
from App.models.db import User, Log
from App.special import *
from App.services.logs import LogService
from sqlalchemy import select, exists
import hashlib

__all__ = (
    'UserService',
)


class UserService:
    __slots__ = ('db',)

    def __init__(self, db_session: AsyncDbSession):
        self.db = db_session

    async def post(self, data: SignUpPostData) -> User:
        """ Auto-commit.
            Raises:
                ALREADY_USED_ERR: 'login',
                ...
        """
        login = data.login.strip()
        first_name = data.first_name.strip()
        last_name = data.last_name.strip()

        # TODO: many many checks

        if await self.db.query_scalar(bool, exists().where(User.login == login)):
            await LogService(self.db).write_log(
                Log.Kind.USER_REGISTER_FAILURE,
                more=f"login:{login}"
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

        await LogService(self.db).write_log(
            Log.Kind.USER_REGISTER_SUCCESS,
            user.id
        )  # + commit

        return user

    async def patch(self, user: User, data: UserSelfPatchData) -> User:
        """ Auto-commit.
            Raises: ...
        """
        return user
