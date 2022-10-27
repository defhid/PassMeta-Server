__all__ = (
    'JwtSession',
    'RequestInfo',
)

from starlette.responses import Response, StreamingResponse
from pydantic import BaseModel
from fastapi import Request
from datetime import datetime

from App.models.dto.mapping import ResultMapping
from App.models.okbad import *
from App.settings import DEBUG
from App.translate import Locale


class JwtSession:
    __slots__ = ('user_id', 'secret_key', 'expires_on')

    def __init__(self, user_id: int, secret_key: str, expires_on: datetime):
        self.user_id = user_id
        self.secret_key = secret_key
        self.expires_on = expires_on


class RequestInfo:
    __slots__ = ('_request', '_locale', '_session')

    def __init__(self, request: Request, locale: str | None, session: JwtSession | None):
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
    def user_id(self) -> int | None:
        return self._session.user_id if self._session is not None else None

    def make_response(self, result: Result, data: BaseModel | list[BaseModel] = None) -> Response:
        return PydanticJsonResponse(
            ResultMapping.to_dto(result, self.locale, data),
            result.code.response_status_code
        )

    @classmethod
    def make_bytes_response(cls, data: bytes) -> Response:
        return StreamingResponse(data)

    def ensure_user_is_authorized(self):
        """ Raises: AUTH_ERR """
        if self._session is None:
            raise Bad(None, AUTH_ERR)


class PydanticJsonResponse(Response):
    media_type = "application/json"

    def __init__(self, content: BaseModel, status_code: int) -> None:
        super().__init__(content, status_code)

    if DEBUG:
        def render(self, content: BaseModel) -> bytes:
            return content.json(indent=4).encode("utf-8")
    else:
        def render(self, content: BaseModel) -> bytes:
            return content.json(indent=None).encode("utf-8")
