from starlette.responses import JSONResponse
from fastapi import Request

from App.translate import OK_BAD_MESSAGES_TRANSLATE_PACK, Locale, get_package_text
from App.models.db import Session
from App.special import *

__all__ = (
    'RequestInfo',
    'PageRequest',
    'PageResult',
    'PassFilePath',
)


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
        d = result.as_dict(lambda code: get_package_text(OK_BAD_MESSAGES_TRANSLATE_PACK, code, self.locale, code.name))
        if data is not None:
            d['data'] = data
        return JSONResponse(d, status_code=result.code.response_status_code)

    def ensure_user_is_authorized(self):
        """ Raises: AUTH_ERR """
        if self._session is None:
            raise Bad(None, AUTH_ERR)


class PageRequest:
    def __init__(self, offset: int, limit: int):
        self.offset = offset
        self.limit = limit


class PageResult(dict):
    __slots__ = ()

    def __init__(self, lst: List, total: int, offset: int, limit: int):
        super().__init__(list=lst, total=total, offset=offset, limit=limit)


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
