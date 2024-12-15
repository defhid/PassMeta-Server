from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError

from App.models.okbad import Result, UNPROCESSABLE_ERR, MORE, Bad, SERVER_ERR
from App.settings import DEBUG
from App.utils.logging import LoggerFactory
from App.utils.request import RequestUtils


def register_exception_middleware(app: FastAPI, request_utils: RequestUtils):
    logger = LoggerFactory.get_named("ROOT")

    def log_error(path: str, exception: Exception):
        logger.error("Request error, url={0}", path, ex=exception)

    def log_warn(path: str, exception: Result):
        logger.info("Request error, url={0}, code={1}, more={2}", path, exception.code.name, exception.more)

    @app.middleware("http")
    async def handler(request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except Result as ex:
            if DEBUG:
                log_warn(request.url.path, ex)
            return request_utils.build_request_info_without_session(request).make_result_response(ex)

        except RequestValidationError as ex:
            if DEBUG:
                log_error(request.url.path, ex)
            return request_utils.build_request_info_without_session(request).make_result_response(
                Bad(UNPROCESSABLE_ERR, MORE.info("schema: " + str(ex.errors()))))

        except Exception as ex:
            log_error(request.url.path, ex)
            return request_utils.build_request_info_without_session(request).make_result_response(
                Bad(SERVER_ERR, MORE.info(str(ex)) if ex.args else None))
