from App.models.db import Session
from App.special import Bad, AUTH_ERR
from typing import Optional
from fastapi import Request

__all__ = (
    'RequestInfo',
)


class RequestInfo:
    __slots__ = ('_request', '_session')

    def __init__(self, request: Request, session: Optional[Session]):
        self._request = request
        self._session = session

    @property
    def request(self) -> Request:
        return self._request

    @property
    def session(self) -> Session:
        return self._session

    @property
    def user_id(self) -> Optional[bool]:
        return self._session.user_id if self._session is not None else None

    def ensure_user_is_authorized(self):
        """ Raises: AUTH_ERR """
        if self._session is None:
            raise Bad(None, AUTH_ERR)
