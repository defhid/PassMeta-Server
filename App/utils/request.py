from App.models.entities import RequestInfo, PageRequest
from App.services import AuthService
from App.utils.db import DbUtils

from typing import Generator, Optional
from pydantic import conint
from starlette.requests import Request

__all__ = (
    'RequestUtils',
)


class RequestUtils:
    __slots__ = ('_db_utils', 'db')

    def __init__(self, db_utils: DbUtils):
        self._db_utils = db_utils

    async def init(self) -> 'RequestUtils':
        """ Takes a connection from db utils and returns self.
        """
        self.db = await self._db_utils.resolve_connection()
        return self

    async def dispose(self):
        """ Releases taken connection back to db utils.
        """
        await self._db_utils.release_connection(self.db)

    async def request_info_maker(self, request: Request, loc: str = None) -> Generator[RequestInfo, None, None]:
        """ Gets request session, creates RequestInfo and yields it.
        """
        yield RequestInfo(request, await AuthService(self.db).get_session(request), loc)

    @staticmethod
    def page_getter(offset: conint(ge=0), limit: conint(gt=0, lt=100)) -> PageRequest:
        return PageRequest(offset, limit)
