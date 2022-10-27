__all__ = ('RequestUtils', )

from App.database import DbUtils
from App.models.entities import RequestInfo
from App.services import AuthService

from starlette.requests import Request


class RequestUtils:
    def __init__(self, db_utils: DbUtils):
        self.db_utils = db_utils

    @classmethod
    def build_request_info_without_session(cls, request: Request) -> RequestInfo:
        """ Creates RequestInfo without session and returns it.
        """
        return RequestInfo(
            request,
            request.query_params.get('lang'),
            None)

    async def build_request_info(self, request: Request) -> RequestInfo:
        """ Gets request session, creates RequestInfo and returns it.
        """
        return RequestInfo(
            request,
            request.query_params.get('lang'),
            await AuthService.get_session(request, self.db_utils.resolve_connection))
