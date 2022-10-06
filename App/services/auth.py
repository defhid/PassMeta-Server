from App.services.base import DbServiceBase
from App.services import UserService
from App.settings import SESSION_LIFETIME_DAYS
from App.special import *
from App.utils.crypto import CryptoUtils

from App.database import User, AuthKey, MakeSql
from App.models.enums import HistoryKind
from App.models.dto import SignInDto
from App.models.entities import RequestInfo, JwtSession

from starlette.requests import Request
from starlette.responses import JSONResponse
from passql import DbConnection
from typing import Callable, Coroutine
from uuid import uuid4
import datetime

__all__ = (
    'AuthService',
)


class AuthService(DbServiceBase):
    __slots__ = ()

    AUTH_KEYS_CACHE: Dict[int, AuthKey] = dict()

    @classmethod
    async def get_session(cls,
                          request: Request,
                          db_resolver: Callable[[], Coroutine[Any, Any, DbConnection]]) -> Optional[JwtSession]:
        token = request.cookies.get('session')
        if not token:
            return None

        data = CryptoUtils.read_jwt(token)
        if not data:
            return None

        try:
            user_id = int(data.get('user_id'))
            secret_key = data.get('secret_key')
            expires_on = datetime.datetime.fromisoformat(data.get('expires_on'))
        except (ValueError, TypeError):
            return None

        if user_id < 1 or (expires_on - datetime.datetime.utcnow()).seconds < 1:
            return None

        auth_key = cls.AUTH_KEYS_CACHE.get(user_id)
        if auth_key is None:
            db = await db_resolver()
            auth_key = await cls.get_or_create_auth_key(user_id, db)

        if secret_key != auth_key.secret_key:
            return None

        return JwtSession(user_id, secret_key, expires_on)

    async def authorize(self, user: User, request_info: RequestInfo) -> JSONResponse:
        auth_key = await self.get_or_create_auth_key(user.id, self.db)

        jwt = self.make_jwt(auth_key)

        response = request_info.make_response(Ok(), data=user.to_dict())
        response.set_cookie('session', jwt, httponly=True)

        return response

    async def reset(self, request_info: RequestInfo, keep_current: bool) -> JSONResponse:
        auth_key = await self.get_or_create_auth_key(request_info.user_id, self.db)
        auth_key.secret_key = uuid4().hex

        await self.db.execute(self._UPDATE_AUTH_KEY, auth_key)

        jwt = self.make_jwt(auth_key) if keep_current else ""

        response = request_info.make_response(Ok())
        response.set_cookie('session', jwt, httponly=True)

        return response

    async def authenticate(self, data: SignInDto, request_info: RequestInfo) -> User:
        """ Raises: NOT_EXIST_ERR, FROZEN_ERR.
        """
        user = await UserService(self.db).get_user_by_login(data.login)

        if user is None:
            await self.history_writer.write(HistoryKind.USER_SIGN_IN_FAILURE, None, None, None)
            raise Bad('user', NOT_EXIST_ERR)

        if not CryptoUtils.check_user_password(data.password, user.pwd):
            await self.history_writer.write(HistoryKind.USER_SIGN_IN_FAILURE, None, user.id, None, "PWD")
            raise Bad('user', NOT_EXIST_ERR)

        if not user.is_active:
            await self.history_writer.write(HistoryKind.USER_SIGN_IN_FAILURE, user.id, user.id, None, "INACTIVE")
            raise Bad('user', FROZEN_ERR)

        await self.history_writer.write(HistoryKind.USER_SIGN_IN_SUCCESS, user.id, user.id, None)
        return user

    @classmethod
    async def get_or_create_auth_key(cls, user_id: int, db: DbConnection) -> AuthKey:
        auth_key = await db.query_first(AuthKey, cls._SELECT_AUTH_KEY_BY_USER_ID, {'user_id': user_id})

        if auth_key is None:
            auth_key = AuthKey()
            auth_key.user_id = user_id
            auth_key.secret_key = uuid4().hex
            await db.execute(cls._INSERT_AUTH_KEY, auth_key)

        cls.AUTH_KEYS_CACHE[user_id] = auth_key

        return auth_key

    @classmethod
    def make_jwt(cls, auth_key: AuthKey) -> str:
        return CryptoUtils.make_jwt({
            'user_id': auth_key.user_id,
            'secret_key': auth_key.secret_key,
            'expires_on': (datetime.datetime.utcnow() + datetime.timedelta(days=SESSION_LIFETIME_DAYS)).isoformat()
        })

    # region SQL

    _SELECT_AUTH_KEY_BY_USER_ID = MakeSql("""
        SELECT id, user_id, secret_key::text
        FROM auth_keys
        WHERE user_id = @user_id
    """)

    _INSERT_AUTH_KEY = MakeSql("""
        INSERT INTO auth_keys (user_id, secret_key)
        VALUES (@user_id, @secret_key::uuid)
    """)

    _UPDATE_AUTH_KEY = MakeSql("""
        UPDATE auth_keys
        SET secret_key = @secret_key::uuid
        WHERE user_id = @user_id
    """)

    # endregion
