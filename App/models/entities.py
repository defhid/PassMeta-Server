__all__ = (
    'JwtSession',
    'RequestInfo',
)

from pydantic import BaseModel
from fastapi import Request, Response
from datetime import datetime, timedelta, UTC

from App.models.dto.mapping import ResultMapping
from App.models.okbad import *
from App.settings import DEBUG, SESSION_REFRESH_MINUTES
from App.translate import Locale
from App.utils.crypto import CryptoUtils


class JwtSession:
    __slots__ = ('user_id', 'secret_key', 'expires_on', 'to_be_refreshed')

    def __init__(self, user_id: int, secret_key: str, expires_on: datetime, to_be_refreshed: bool):
        self.user_id = user_id
        self.secret_key = secret_key
        self.expires_on = expires_on
        self.to_be_refreshed = to_be_refreshed


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

    def _fill_response(self, response: Response) -> Response:
        if self._session is not None and self._session.to_be_refreshed:
            jwt = CryptoUtils.make_jwt({
                'user_id': self._session.user_id,
                'secret_key': self._session.secret_key,
                'valid_until': (datetime.now(UTC) + timedelta(minutes=SESSION_REFRESH_MINUTES)).isoformat(),
                'expires_on': self._session.expires_on.isoformat(),
            })

            response.set_cookie(
                'session',
                jwt,
                httponly=True,
                secure=True,
                samesite="none",
                expires=self._session.expires_on,
            )

        return response

    def make_response(self, data: BaseModel = None) -> Response:
        return self._fill_response(PydanticJsonResponse(data, OK.response_status_code) if data is not None \
            else Response(status_code=OK.response_status_code))

    def make_bytes_response(self, data: bytes) -> Response:
        return self._fill_response(Response(data))

    def make_result_response(self, data: Result) -> Response:
        return self._fill_response(PydanticJsonResponse(
            ResultMapping.to_dto(data, self.locale),
            data.code.response_status_code
        ))

    def ensure_user_is_authorized(self):
        """ Raises: AUTH_ERR """
        if self._session is None:
            raise Bad(AUTH_ERR)


class PydanticJsonResponse(Response):
    media_type = "application/json"

    def __init__(self, content: BaseModel, status_code: int) -> None:
        super().__init__(content, status_code)

    if DEBUG:
        def render(self, content: BaseModel) -> bytes:
            return content.model_dump_json(indent=4, exclude_unset=True, by_alias=True).encode("utf-8")
    else:
        def render(self, content: BaseModel) -> bytes:
            return content.model_dump_json(indent=None, exclude_unset=True, by_alias=True).encode("utf-8")
