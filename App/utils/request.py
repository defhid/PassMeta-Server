__all__ = ('RequestUtils', )

from App.database import DbUtils
from App.models.entities import RequestInfo
from App.services import AuthService
from App.utils.logging import LoggerFactory
from starlette.requests import Request

class RequestUtils:
    logger = LoggerFactory.get_named("HISTORY WRITER")

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
        try:
            session = await AuthService.get_session(request, self.db_utils)
        except Exception as e:
            self.logger.error("Failed to get session from request", ex=e)
            session = None

        return RequestInfo(request, request.query_params.get('lang'), session)
