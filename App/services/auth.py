from App.models.okbad import *
from App.services.base import DbServiceBase
from App.services import UserService
from App.settings import SESSION_LIFETIME_DAYS
from App.utils.crypto import CryptoUtils

from App.database import User, AuthKey, MakeSql
from App.models.enums import HistoryKind
from App.models.dto.requests import SignInDto
from App.models.entities import RequestInfo, JwtSession
from App.models.dto.mapping import UserMapping

from starlette.requests import Request
from starlette.responses import Response
from passql import DbConnection
from typing import Callable, Coroutine, Any
from uuid import uuid4
import datetime

__all__ = (
    'AuthService',
)


class AuthService(DbServiceBase):
    __slots__ = ()

    @classmethod
    async def get_session(cls,
                          request: Request,
                          db_resolver: Callable[[], Coroutine[Any, Any, DbConnection]]) -> JwtSession | None:
        token = request.cookies.get('session')
        if not token:
            return None

        data = CryptoUtils.read_jwt(token)
        if not data:
            return None

        try:
            user_id = int(data.get('user_id'))
            secret_key = data.get('secret_key')
            valid_until = datetime.datetime.fromisoformat(data.get('valid_until'))
            expires_on = datetime.datetime.fromisoformat(data.get('expires_on'))
        except (ValueError, TypeError):
            return None

        if user_id < 1 or (expires_on - datetime.datetime.utcnow()).seconds < 1:
            return None

        if (valid_until - datetime.datetime.utcnow()).seconds < 1:
            db = await db_resolver()
            auth_key = await cls.get_or_create_auth_key(user_id, db)

            if secret_key != auth_key.secret_key:
                return None

            return JwtSession(
                user_id,
                secret_key,
                datetime.datetime.utcnow() + datetime.timedelta(days=SESSION_LIFETIME_DAYS),
                to_be_refreshed=True,
            )

        return JwtSession(user_id, secret_key, expires_on, to_be_refreshed=False)

    async def authorize(self, user: User) -> Response:
        try:
            auth_key = await self.get_or_create_auth_key(user.id, self.db)

            self.request.session = JwtSession(
                auth_key.user_id,
                auth_key.secret_key,
                datetime.datetime.utcnow() + datetime.timedelta(days=SESSION_LIFETIME_DAYS),
                to_be_refreshed=True,
            )

            response = self.request.make_response(UserMapping.to_dto(user))
        except Exception:
            await self.history_writer.write(HistoryKind.USER_SIGN_IN_FAILURE, user.id, None, user_id=user.id)
            raise

        await self.history_writer.write(HistoryKind.USER_SIGN_IN_SUCCESS, user.id, None, user_id=user.id)

        return response

    @staticmethod
    def reset(request_info: RequestInfo) -> Response:
        if request_info.session:
            request_info.session = JwtSession(
                request_info.session.user_id,
                request_info.session.secret_key,
                datetime.datetime.utcnow(),
                to_be_refreshed=True,
            )

        return request_info.make_response()

    async def reset_all(self, request_info: RequestInfo, keep_current: bool) -> Response:
        auth_key = await self.get_or_create_auth_key(request_info.user_id, self.db)
        auth_key.secret_key = uuid4().hex

        async with self.db.transaction():
            await self.db.query_scalar(str, self._UPDATE_AUTH_KEY, auth_key)

            await self.history_writer.write(HistoryKind.USER_SESSIONS_RESET, auth_key.user_id, None)

        request_info.session = JwtSession(
            auth_key.user_id,
            auth_key.secret_key,
            datetime.datetime.utcnow() + datetime.timedelta(days=SESSION_LIFETIME_DAYS if keep_current else 0),
            to_be_refreshed=True,
        )

        return request_info.make_response()

    async def authenticate(self, data: SignInDto) -> User:
        """ Raises: NOT_EXIST_ERR, FROZEN_ERR.
        """
        user = await UserService(self.db, self.request).get_user_by_login(data.login)

        if user is None:
            await self.history_writer.write(HistoryKind.USER_SIGN_IN_FAILURE, None, None, None)
            raise Bad(VALIDATION_ERR, MORE.not_found(WHAT.USER.user))

        if not CryptoUtils.check_user_password(data.password, user.pwd):
            await self.history_writer.write(HistoryKind.USER_SIGN_IN_FAILURE, user.id, None, "PWD")
            raise Bad(VALIDATION_ERR, MORE.not_found(WHAT.USER.user))

        if not user.is_active:
            await self.history_writer.write(HistoryKind.USER_SIGN_IN_FAILURE, user.id, None, "INACTIVE")
            raise Bad(AUTH_ERR, MORE.frozen(WHAT.USER.user))

        return user

    @classmethod
    async def get_or_create_auth_key(cls, user_id: int, db: DbConnection) -> AuthKey:
        auth_key = await db.query_first(AuthKey, cls._SELECT_AUTH_KEY_BY_USER_ID, {'user_id': user_id})

        if auth_key is None:
            auth_key = AuthKey()
            auth_key.user_id = user_id
            auth_key.secret_key = uuid4().hex
            await db.execute(cls._INSERT_AUTH_KEY, auth_key)

        auth_key.secret_key = auth_key.secret_key.replace('-', '')
        return auth_key

    # region SQL

    _SELECT_AUTH_KEY_BY_USER_ID = MakeSql("""
        SELECT user_id, secret_key::text
        FROM auth_keys
        WHERE user_id = #user_id
    """)

    _INSERT_AUTH_KEY = MakeSql("""
        INSERT INTO auth_keys (user_id, secret_key)
        VALUES (#user_id, #secret_key::uuid)
    """)

    _UPDATE_AUTH_KEY = MakeSql("""
        UPDATE auth_keys
        SET secret_key = #secret_key::uuid
        WHERE user_id = #user_id
    """)

    # endregion
