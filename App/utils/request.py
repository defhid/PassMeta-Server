from App.models.entities import RequestInfo
from App.services import AuthService
from App.utils.db import DbUtils

from starlette.requests import Request

__all__ = (
    'RequestUtils',
)


class RequestUtils:
    __slots__ = ('_db_utils', )

    def __init__(self, db_utils: DbUtils):
        self._db_utils = db_utils

    @staticmethod
    def build_request_info_without_session(request: Request) -> RequestInfo:
        """ Creates RequestInfo without session and returns it.
        """
        return RequestInfo(request, request.query_params.get('lang'), None)

    async def build_request_info(self, request: Request) -> RequestInfo:
        """ Gets request session, creates RequestInfo and returns it.
        """
        exact, session = AuthService.get_cached_session(request)
        if not exact:
            async with self._db_utils.context_connection() as db:
                session = await AuthService(db).get_session(request)

        return RequestInfo(request, request.query_params.get('lang'), session)
