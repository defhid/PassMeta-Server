import datetime

from starlette.responses import JSONResponse
from fastapi import Request

from App.translate import Locale
from App.special import *

__all__ = (
    'JwtSession',
    'RequestInfo',
)


class JwtSession:
    __slots__ = ('user_id', 'secret_key', 'expires_on')

    def __init__(self, user_id: int, secret_key: str, expires_on: datetime.datetime):
        self.user_id = user_id
        self.secret_key = secret_key
        self.expires_on = expires_on


class RequestInfo:
    __slots__ = ('_request', '_locale', '_session')

    def __init__(self, request: Request, locale: Optional[str], session: Optional[JwtSession]):
        self._request = request
        self._session = session
        self._locale = locale

    @property
    def request(self) -> Request:
        return self._request

    @property
    def locale(self) -> str:
        return self._locale if self._locale else Locale.DEFAULT

    @property
    def session(self) -> JwtSession:
        return self._session

    @session.setter
    def session(self, value):
        if self._session is None:
            self._session = value

    @property
    def user_id(self) -> Optional[int]:
        return self._session.user_id if self._session is not None else None

    def make_response(self, result: Result, data: Any = None) -> JSONResponse:
        return JSONResponse(result.as_dict(self.locale, data), status_code=result.code.response_status_code)

    def ensure_user_is_authorized(self):
        """ Raises: AUTH_ERR """
        if self._session is None:
            raise Bad(None, AUTH_ERR)
