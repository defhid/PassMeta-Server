from App.controllers.auth_controllers import build_auth_controllers
from App.controllers.di import Deps
from App.controllers.general_controllers import build_general_controllers
from App.controllers.history_controllers import build_history_controllers
from App.controllers.passfile_controllers import build_passfile_controllers
from App.controllers.user_controllers import build_user_controllers

from App.database import DbUtils, Migrator

from App.utils.logging import LoggerFactory, init_logging
from App.utils.passfile import PassFileUtils
from App.utils.request import RequestUtils
from App.utils.scheduler import Scheduler, SchedulerTask

from App.settings import *
from App.services import HistoryService
from App.models.okbad import *

from fastapi import FastAPI, Request, Depends
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware


db_utils = DbUtils(DB_CONNECTION_POOL_MAX_SIZE)
request_utils = RequestUtils(db_utils)

scheduler = Scheduler(period_minutes=10)

app = FastAPI(debug=DEBUG, docs_url="/docs", root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=UVICORN_CORS_PATTERN,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# region Exceptions handling

class RouteWithErrorsLogging(APIRoute):
    logger = LoggerFactory.get_named("ROOT")

    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        def log_error(path: str, exception: Exception):
            self.logger.error("Request error, url={0}", path, ex=exception)

        def log_warn(path: str, exception: Result):
            self.logger.info("Request error, url={0}, code={1}, more={2}", path, exception.code.name, exception.more)

        async def custom_route_handler(request: Request):
            try:
                return await original_route_handler(request)
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

        return custom_route_handler

# endregion


# region Event handlers

@app.on_event("startup")
async def on_startup():
    init_logging('uvicorn.error')

    await db_utils.init()

    if CHECK_MIGRATIONS_ON_STARTUP:
        async with db_utils.context_connection() as db:
            await Migrator(db).run()

    PassFileUtils.ensure_folders_created()

    scheduler.add(SchedulerTask(
        'OHISCHECK',
        active=True,
        single=False,
        interval_minutes=HISTORY_CHECKING_INTERVAL_DAYS * 24 * 60,
        start_now=CHECK_HISTORY_ON_STARTUP,
        func=HistoryService.scheduled__check_old_histories
    ))

    scheduler.run()


@app.on_event("shutdown")
async def on_shutdown():
    scheduler.stop()
    await db_utils.dispose()

# endregion

deps = Deps()
deps.DB = Depends(db_utils.connection_maker, use_cache=False)
deps.REQUEST_INFO = Depends(request_utils.build_request_info, use_cache=False)
deps.REQUEST_INFO_WS = Depends(request_utils.build_request_info_without_session, use_cache=False)

controllers = [
    build_auth_controllers(deps),
    build_general_controllers(deps),
    build_history_controllers(deps),
    build_passfile_controllers(deps),
    build_user_controllers(deps),
]

for router in controllers:
    router.route_class = RouteWithErrorsLogging
    app.include_router(router)
