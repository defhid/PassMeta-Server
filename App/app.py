from App.controllers.auth_controllers import build_auth_controllers
from App.controllers.di import Deps
from App.controllers.general_controllers import build_general_controllers
from App.controllers.history_controllers import build_history_controllers
from App.controllers.passfile_controllers import build_passfile_controllers
from App.controllers.user_controllers import build_user_controllers

from App.database import DbUtils, Migrator
from App.middlewares.exception_middleware import register_exception_middleware

from App.utils.logging import init_logging
from App.utils.passfile import PassFileUtils
from App.utils.request import RequestUtils
from App.utils.scheduler import Scheduler, SchedulerTask

from App.settings import *
from App.services import HistoryService

from fastapi import FastAPI, Depends
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
    app.include_router(router)

register_exception_middleware(app, request_utils)
