from App.models.db import Session
from App.special import *
from fastapi import Request

__all__ = (
    'RequestInfo',
    'PageRequest',
    'PageResult',
)


class RequestInfo:
    __slots__ = ('_request', '_session', '_loc')

    def __init__(self, request: Request, session: Optional[Session], locale: Optional[str]):
        self._request = request
        self._session = session
        self._loc = locale if Locales.contains_id(locale) else Locales.DEFAULT.code

    @property
    def request(self) -> Request:
        return self._request

    @property
    def session(self) -> Session:
        return self._session

    @property
    def loc(self) -> str:
        return self._loc

    @property
    def user_id(self) -> Optional[bool]:
        return self._session.user_id if self._session is not None else None

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
