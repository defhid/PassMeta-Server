from fastapi import Request
from starlette.responses import JSONResponse
from sqlalchemy import select
from typing import Optional
import hashlib
import datetime

from App.special import *
from App.utils.db import *
from App.models.db import Session, User, Log
from App.models.request import SignInPostData
from App.settings import SESSION_AGE
from App.services.logs import LogService


__all__ = (
    'AuthService',
)


class AuthService:
    __slots__ = ('db',)

    def __init__(self, db_session: AsyncDbSession):
        self.db = db_session

    async def get_session(self, request: Request) -> Optional[Session]:
        """ Auto-commit.
        """
        session_id = request.cookies.get('session')
        if session_id:
            session = await self.db.query_first(Session, select(Session).where(Session.id == session_id))
            if (datetime.datetime.now() - session.created_on).days > SESSION_AGE:
                await self.db.delete(session)
                await self.db.commit()
            else:
                return session
        return None

    async def get_user(self, request: Request) -> User:
        """ Auto-commit: handle session.
            Raises: AUTH_ERR.
        """
        session = await self.get_session(request)
        if session:
            user = await self.db.query_first(User, select(User).where(User.id == session.user_id))
            if user:
                if user.is_active:
                    return user
                else:
                    raise Bad(None, NOT_AVAILABLE, MORE.text("Учётная запись неактивна!"))
            else:
                await self.db.delete(user)
                await self.db.commit()

        raise Bad(None, AUTH_ERR)

    async def authorize(self, user: User, request: Request) -> JSONResponse:
        """ Auto-commit.
        """
        session_id = request.cookies.get('session')

        if session_id:
            session = await self.db.query_first(Session, select(Session).where(Session.id == session_id))
            if session is not None:
                await self.db.delete(session)

        session = Session(user_id=user.id)

        self.db.add(session)
        await self.db.commit()

        response = Ok().as_response(data=user.to_dict())
        response.set_cookie('session', session.id, httponly=True)

        return response

    async def authenticate(self, data: SignInPostData, request: Request) -> User:
        """ Auto-commit: logs.
            Raises: NOT_EXIST_ERR.
        """
        password_hash = hashlib.sha512(data.password.encode('utf-8')).hexdigest()

        user = await self.db.query_first(
            User, select(User).where(User.login == data.login.strip() and User.pwd == password_hash)
        )
        if user:
            if user.is_active:
                await LogService(self.db).write_log(
                    Log.Kind.USER_SIGN_IN_SUCCESS,
                    entity_id=user.id,
                    more=f"{request.client.host}:{request.client.port}"
                )
                return user
            else:
                await LogService(self.db).write_log(
                    Log.Kind.USER_SIGN_IN_FAILURE,
                    more=f"{request.client.host}:{request.client.port},inactive,login:{data.login}"
                )
                raise Bad('user', NOT_AVAILABLE, MORE.text("Учётная запись неактивна!"))
        else:
            await LogService(self.db).write_log(
                Log.Kind.USER_SIGN_IN_FAILURE,
                more=f"{request.client.host}:{request.client.port},login:{data.login}"
            )
            raise Bad('user', NOT_EXIST_ERR)

    async def sign_out(self, request: Request):
        """ Auto-commit. """
        session = self.get_session(request)
        if session:
            await self.db.delete(session)
            await self.db.commit()
