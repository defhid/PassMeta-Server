from App.models.entities import RequestInfo, PageRequest
from App.services import AuthService
from App.utils.db import DbUtils

from typing import Generator
from pydantic import conint
from starlette.requests import Request

__all__ = (
    'RequestUtils',
)


class RequestUtils:
    __slots__ = ('_db_utils', )

    def __init__(self, db_utils: DbUtils):
        self._db_utils = db_utils

    async def request_info_maker(self, request: Request) -> Generator[RequestInfo, None, None]:
        """ Gets request session, creates RequestInfo and yields it.
        """
        async with self._db_utils.context_connection() as db:
            session = await AuthService(db).get_session(request)

        yield RequestInfo(request, session)

    @staticmethod
    def page_getter(offset: conint(ge=0), limit: conint(gt=0, lt=100)) -> PageRequest:
        return PageRequest(offset, limit)
