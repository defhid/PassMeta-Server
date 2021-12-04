from App.services.base import DbServiceBase
from App.settings import SESSION_LIFETIME_DAYS, SESSION_CACHE_SIZE
from App.special import *

from App.models.db import Session, User, History
from App.models.request import SignInPostData
from App.models.entities import RequestInfo

from App.utils.db import MakeSql
from App.utils.scheduler import SchedulerTask

from starlette.requests import Request
from starlette.responses import JSONResponse
import hashlib
import datetime

__all__ = (
    'AuthService',
)


class AuthService(DbServiceBase):
    __slots__ = ()

    __CACHE: LRUCache[str, Session] = LRUCache(SESSION_CACHE_SIZE)

    async def get_session(self, request: Request) -> Optional[Session]:
        session_id = request.cookies.get('session')
        if not session_id:
            return None

        session = self.__CACHE.get(session_id, None)
        if session is None:
            session = await self.db.query_first(Session, self._SELECT_SESSION_BY_ID, {'id': session_id})

        if session:
            if (datetime.datetime.now() - session.created_on).days > SESSION_LIFETIME_DAYS:
                self.__CACHE.pop(session_id, None)
                await self.db.execute(self._SELECT_SESSION_BY_ID, session)
            else:
                return session

        return None

    async def authorize(self, user: User, request_info: RequestInfo) -> JSONResponse:
        session_id = request_info.request.cookies.get('session')

        if session_id:
            await self.db.execute(self._DELETE_SESSION_BY_ID, {'id': session_id})

        session = await self.db.query_first(Session, self._INSERT_SESSION, {'user_id': user.id})
        self.__CACHE.put(session.id, session)

        response = Ok().as_response(data=user.to_dict())
        response.set_cookie('session', session.id, httponly=True)

        return response

    async def authenticate(self, data: SignInPostData, request_info: RequestInfo) -> User:
        """ Raises: NOT_EXIST_ERR, FROZEN_ERR.
        """
        user = await self.db.query_first(User, self._SELECT_USER_BY_LOGIN, {'login': data.login.strip()})

        if user is None:
            await self.history_writer.write(History.Kind.USER_SIGN_IN_FAILURE,
                                            None, None, more=f"login:{data.login}", request=request_info)
            raise Bad('user', NOT_EXIST_ERR)

        if not self.check_password(data.password, user.pwd):
            await self.history_writer.write(History.Kind.USER_SIGN_IN_FAILURE,
                                            None, user.id, more="PWD", request=request_info)
            raise Bad('user', NOT_EXIST_ERR)

        if not user.is_active:
            await self.history_writer.write(History.Kind.USER_SIGN_IN_FAILURE,
                                            user.id, user.id, more=f"INACTIVE,login:{data.login}", request=request_info)
            raise Bad('user', FROZEN_ERR)

        await self.history_writer.write(History.Kind.USER_SIGN_IN_SUCCESS,
                                        user.id, user.id, request=request_info)
        return user

    async def sign_out(self, request_info: RequestInfo):
        """ Auto-commit. """
        session_id = request_info.request.cookies.get('session')
        if session_id:
            self.__CACHE.pop(session_id, None)
            await self.db.execute(self._DELETE_SESSION_BY_ID, {'id': session_id})

    @classmethod
    def check_password(cls, raw_password: str, pwd: str) -> bool:
        return hashlib.sha512(raw_password.encode('utf-8')).hexdigest() == pwd

    @classmethod
    async def scheduled__check_old_sessions(cls, context: 'SchedulerTask.Context'):
        expired = datetime.datetime.now() - datetime.timedelta(days=SESSION_LIFETIME_DAYS)

        async with context.db_utils.context_connection() as db:
            session_ids = await db.query_values_list(str, cls._DELETE_OLD_SESSIONS, {'expire_date': expired})

        for session_id in session_ids:
            cls.__CACHE.pop(session_id)

    # region SQL

    _SELECT_SESSION_BY_ID = MakeSql("""SELECT * FROM session WHERE id = @id""")

    _INSERT_SESSION = MakeSql("""INSERT INTO session (user_id) VALUES (@user_id) RETURNING *""")

    _SELECT_USER_BY_LOGIN = MakeSql("""SELECT * FROM "user" WHERE login = @login""")

    _DELETE_SESSION_BY_ID = MakeSql("""DELETE FROM session WHERE id = @id""")

    _DELETE_OLD_SESSIONS = MakeSql("""DELETE FROM session WHERE created_on < @expire_date RETURNING id""")

    # endregion
