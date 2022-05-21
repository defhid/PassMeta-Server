from App.services.base import DbServiceBase
from App.services import UserService
from App.settings import SESSION_LIFETIME_DAYS
from App.special import *
from App.utils.crypto import CryptoUtils

from App.database import User
from App.models.enums import HistoryKind
from App.models.dto import SignInDto
from App.models.entities import RequestInfo, Session

from starlette.requests import Request
from starlette.responses import JSONResponse
import datetime

__all__ = (
    'AuthService',
)


class AuthService(DbServiceBase):
    __slots__ = ()

    @classmethod
    def get_session(cls, request: Request) -> Optional[Session]:
        token = request.cookies.get('session')
        if not token:
            return None

        data = CryptoUtils.read_jwt(token)
        if not data:
            return None

        try:
            user_id = int(data.get('user_id'))
            created_on = datetime.datetime.fromisoformat(data.get('created_on'))
        except ValueError:
            return None

        if user_id < 1 or (datetime.datetime.utcnow() - created_on).days > SESSION_LIFETIME_DAYS:
            return None

        return Session(user_id, created_on)

    @classmethod
    def authorize(cls, user: User, request_info: RequestInfo) -> JSONResponse:
        session = CryptoUtils.make_jwt({
            'user_id': user.id,
            'created_on': datetime.datetime.utcnow().isoformat()
        })

        response = request_info.make_response(Ok(), data=user.to_dict())
        response.set_cookie('session', session, httponly=True)

        return response

    async def authenticate(self, data: SignInDto, request_info: RequestInfo) -> User:
        """ Raises: NOT_EXIST_ERR, FROZEN_ERR.
        """
        user = await UserService(self.db).get_user_by_login(data.login)

        if user is None:
            await self.history_writer.write(HistoryKind.USER_SIGN_IN_FAILURE,
                                            None, None, more=f"login:{data.login}", request=request_info)
            raise Bad('user', NOT_EXIST_ERR)

        if not CryptoUtils.check_user_password(data.password, user.pwd):
            await self.history_writer.write(HistoryKind.USER_SIGN_IN_FAILURE,
                                            None, user.id, more="PWD", request=request_info)
            raise Bad('user', NOT_EXIST_ERR)

        if not user.is_active:
            await self.history_writer.write(HistoryKind.USER_SIGN_IN_FAILURE,
                                            user.id, user.id, more=f"INACTIVE,login:{data.login}", request=request_info)
            raise Bad('user', FROZEN_ERR)

        await self.history_writer.write(HistoryKind.USER_SIGN_IN_SUCCESS,
                                        user.id, user.id, request=request_info)
        return user
