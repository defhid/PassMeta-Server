import datetime

from starlette.responses import JSONResponse
from fastapi import Request

from App.translate import Locale
from App.special import *

__all__ = (
    'Session',
    'RequestInfo',
    'PassFilePath',
)


class Session:
    __slots__ = ('user_id', 'created_on')

    def __init__(self, user_id: int, created_on: datetime.datetime):
        self.user_id = user_id
        self.created_on = created_on


class RequestInfo:
    __slots__ = ('_request', '_locale', '_session')

    def __init__(self, request: Request, locale: Optional[str], session: Optional[Session]):
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
    def session(self) -> Session:
        return self._session

    @property
    def user_id(self) -> Optional[bool]:
        return self._session.user_id if self._session is not None else None

    def make_response(self, result: Result, data: Any = None) -> JSONResponse:
        return JSONResponse(result.as_dict(self.locale, data), status_code=result.code.response_status_code)

    def ensure_user_is_authorized(self):
        """ Raises: AUTH_ERR """
        if self._session is None:
            raise Bad(None, AUTH_ERR)


class PassFilePath:
    __slots__ = ('id', 'version', 'full_path')

    def __init__(self, filename: str, full_path: str):
        parts = filename.split('v')

        try:
            self.id = int(parts[0])
        except ValueError:
            self.id = None

        try:
            self.version = int(parts[1].split('.')[0])
        except ValueError:
            self.version = -1

        self.full_path = full_path
