from App.models.entities import RequestInfo
from App.services import AuthService

from starlette.requests import Request

__all__ = (
    'RequestUtils',
)


class RequestUtils:
    @classmethod
    def build_request_info_without_session(cls, request: Request) -> RequestInfo:
        """ Creates RequestInfo without session and returns it.
        """
        return RequestInfo(request, request.query_params.get('lang'), None)

    @classmethod
    async def build_request_info(cls, request: Request) -> RequestInfo:
        """ Gets request session, creates RequestInfo and returns it.
        """
        return RequestInfo(request, request.query_params.get('lang'), AuthService.get_session(request))
