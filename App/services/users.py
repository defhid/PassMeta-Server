from App.models.request import SignUpPostData, UserSelfPatchData
from App.utils.db import AsyncSession
from App.models.db import User
from App.special import *
from sqlalchemy.future import select
import hashlib

__all__ = (
    'UserService',
)


class UserService:
    @classmethod
    async def post(cls, data: SignUpPostData, db_session: AsyncSession) -> User:
        """ Warning: auto-commit. """
        login = data.login.strip()
        first_name = data.first_name.strip()
        last_name = data.last_name.strip()

        # TODO: many many checks

        if (await db_session.execute(select(User).where(User.login == login))).first():
            raise Bad('login', ALREADY_USED_ERR)

        user = User(
            login=login,
            pwd=hashlib.sha512(data.password.encode('utf-8')).hexdigest(),
            first_name=first_name,
            last_name=last_name,
        )

        db_session.add(user)
        await db_session.commit()

        return user

    @classmethod
    async def patch(cls, user: User, data: UserSelfPatchData, db_session: AsyncSession) -> User:
        """ Warning: auto-commit. """
        return user
