from fastapi import Request
from starlette.responses import JSONResponse
from sqlalchemy import select
from typing import Optional
import hashlib

from App.utils.db import *
from App.models.db import Session, User
from App.special import *
from App.models.request import SignInPostData

__all__ = (
    'AuthService',
)


class AuthService:
    @classmethod
    async def try_get_user_async(cls, request: Request, db_session: AsyncSession) -> Optional[User]:
        session_id = request.cookies.get('session')
        if session_id:
            # TODO: check session date!
            return (await db_session.execute(select(User)
                                             .join(Session, User.id == Session.user_id)
                                             .where(Session.id == session_id))).first()
        return None

    @classmethod
    async def get_user_async(cls, request: Request, db_session: AsyncSession) -> User:
        """ Raises: AUTH_ERR. """
        session_id = request.cookies.get('session')
        if session_id:
            # TODO: check session date!
            user = (await db_session.execute(select(User)
                                             .join(Session, User.id == Session.user_id)
                                             .where(Session.id == session_id))).first()
            if user is not None:
                return user

        raise Bad(None, AUTH_ERR)

    @classmethod
    async def authorize(cls, user: User, request: Request, db_session: AsyncSession) -> JSONResponse:
        """ Warning: auto-commit. """
        session_id = request.cookies.get('session')

        if session_id:
            session = (await db_session.execute(
                select(Session).where(Session.id == session_id)
            )).first()
            if session is not None:
                await db_session.delete(session)

        session = Session(user_id=user.id)

        db_session.add(session)
        await db_session.commit()

        response = JSONResponse(Ok(data=user).dict())
        response.set_cookie('session', session.id, httponly=True)
        return response

    @classmethod
    async def authenticate(cls, data: SignInPostData, db_session: AsyncSession) -> User:
        password_hash = hashlib.sha512(data.password.encode('utf-8')).hexdigest()

        user = (await db_session.execute(
            select(User).where(User.login == data.login.strip() and User.pwd == password_hash)
        )).scalars().first()

        if user is None:
            raise Bad('user', NOT_EXIST_ERR)

        return user

    @classmethod
    async def sign_out(cls, request: Request, db_session: AsyncSession):
        """ Warning: auto-commit """
        session_id = request.cookies.get('session')
        if session_id:
            session = (await db_session.execute(
                select(Session).where(Session.id == session_id)
            )).first()
            if session is not None:
                await db_session.delete(session)
                await db_session.commit()
