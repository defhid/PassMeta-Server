from App.special import *

from App.models.request import *
from App.models.entities import RequestInfo
from App.models.db import check_entities

from App.utils.db import DbUtils
from App.utils.logging import Logger
from App.utils.passfile import PassFileUtils
from App.utils.request import RequestUtils
from App.utils.scheduler import Scheduler, SchedulerTask

from App.settings import *
from App.services import (
    AuthService,
    UserService,
    PassFileService,
    HistoryService,
)

from passql import DbConnection
from fastapi import FastAPI, Request, Depends
from fastapi.routing import APIRoute
from fastapi.exceptions import RequestValidationError


logger = Logger(__file__)

db_utils = DbUtils(DB_CONNECTION_POOL_MAX_SIZE)

request_utils = RequestUtils(db_utils)

scheduler = Scheduler(period_minutes=10)

app = FastAPI(debug=DEBUG)


# region Exceptions handling

class ErrorsLoggingRoute(APIRoute):
    def get_route_handler(self):
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            try:
                return await original_route_handler(request)
            except Result as ex:
                return ex.as_response()
            except RequestValidationError as ex:
                return Bad(None, BAD_REQUEST_ERR, MORE.info({"validation error": ex.errors()})).as_response()
            except Exception as ex:
                logger.error("Request error", ex)
                return Bad(None, SERVER_ERR, MORE.text(str(ex)) if ex.args else None).as_response()

        return custom_route_handler


app.router.route_class = ErrorsLoggingRoute

# endregion


# region Event handlers

@app.on_event("startup")
async def on_startup():
    Logger.init('uvicorn.error' if __name__ == '__main__' else 'gunicorn.error')

    await db_utils.init()
    await request_utils.init()

    async with db_utils.context_connection() as db:
        await check_entities(db)

    PassFileUtils.ensure_folders_created()

    scheduler.add(SchedulerTask(
        'SESCHECK',
        active=True,
        single=False,
        interval_minutes=OLD_SESSIONS_CHECKING_INTERVAL_MINUTES,
        start_now=OLD_SESSIONS_CHECKING_ON_STARTUP,
        func=AuthService.scheduled__check_old_sessions
    ))

    scheduler.add(SchedulerTask(
        'APASCHECK',
        active=True,
        single=False,
        interval_minutes=OLD_PASSFILES_CHECKING_INTERVAL_MINUTES,
        start_now=OLD_PASSFILES_CHECKING_ON_STARTUP,
        func=PassFileService.scheduled__check_archived_files
    ))

    scheduler.add(SchedulerTask(
        'OHISCHECK',
        active=True,
        single=False,
        interval_minutes=OLD_HISTORY_CHECKING_INTERVAL_DAYS,
        start_now=OLD_HISTORY_CHECKING_ON_STARTUP,
        func=HistoryService.scheduled__check_old_histories
    ))

    scheduler.run()


@app.on_event("shutdown")
async def on_shutdown():
    scheduler.stop()
    await request_utils.dispose()
    await db_utils.dispose()


# endregion


# region Aliases

GET = app.get
POST = app.post
PATCH = app.patch
PUT = app.put
DELETE = app.delete

DB = Depends(db_utils.connection_maker)
REQUEST_INFO = Depends(request_utils.request_info_maker)

# endregion


# region Auth

@POST("/auth/sign-in")
async def ctrl(body: SignInPostData,
               request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    service = AuthService(db)
    user = await service.authenticate(body, request)
    return await service.authorize(user, request)


@POST("/auth/sign-out")
async def ctrl(request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    await AuthService(db).sign_out(request)
    return Ok().as_response()

# endregion


# region Passfile

@GET("/passfiles/list")
async def ctrl(request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    request.ensure_user_is_authorized()
    passfiles = await PassFileService(db).get_user_passfiles(await request.session.get_user(db))
    converted = list(map(lambda p: p.to_dict(), passfiles))
    return Ok().as_response(data=converted)


@GET("/passfiles/{passfile_id}")
async def ctrl(passfile_id: int,
               request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    request.ensure_user_is_authorized()
    passfile, data = await PassFileService(db).get_file(passfile_id, request)
    return Ok().as_response(data=passfile.to_dict(data))


@POST("/passfiles/new")
async def ctrl(body: PassfilePostData,
               request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    request.ensure_user_is_authorized()
    passfile = await PassFileService(db).add_file(body, request)
    return Ok().as_response(data=passfile.to_dict())


@PATCH("/passfiles/{passfile_id}/info")
async def ctrl(passfile_id: int, body: PassfileInfoPatchData,
               request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    request.ensure_user_is_authorized()
    passfile = await PassFileService(db).edit_file_info(passfile_id, body, request)
    return Ok().as_response(data=passfile.to_dict())


@PATCH("/passfiles/{passfile_id}/smth")
async def ctrl(passfile_id: int, body: PassfileSmthPatchData,
               request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    request.ensure_user_is_authorized()
    passfile = await PassFileService(db).edit_file_smth(passfile_id, body, request)
    return Ok().as_response(data=passfile.to_dict())


@PUT("/passfiles/{passfile_id}/to/archive")
async def ctrl(passfile_id: int,
               request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    request.ensure_user_is_authorized()
    await PassFileService(db).archive_file(passfile_id, request)
    return Ok().as_response()


@PUT("/passfiles/{passfile_id}/to/actual")
async def ctrl(passfile_id: int,
               request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    request.ensure_user_is_authorized()
    await PassFileService(db).unarchive_file(passfile_id, request)
    return Ok().as_response()


@DELETE("/passfiles/{passfile_id}")
async def ctrl(passfile_id: int, body: PassfileDeleteData,
               request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    request.ensure_user_is_authorized()
    await PassFileService(db).delete_file(passfile_id, body.check_password, request)
    return Ok().as_response()

# endregion


# region Users

@POST("/users/new")
async def ctrl(body: SignUpPostData,
               request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    user = await UserService(db).create_user(body, request)
    return await AuthService(db).authorize(user, request)


@GET("/users/me")
async def ctrl(request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    request.ensure_user_is_authorized()
    user = await request.session.get_user(db)
    return Ok().as_response(data=user.to_dict())


@PATCH("/users/me")
async def ctrl(body: UserPatchData,
               request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    request.ensure_user_is_authorized()
    user = await UserService(db).edit_user(request.user_id, body, request)
    return Ok().as_response(data=user.to_dict())

# endregion


# region info

@GET("/info")
async def ctrl(request: RequestInfo = REQUEST_INFO, db: DbConnection = DB):
    if request.session is not None:
        user = (await request.session.get_user(db)).to_dict()
    else:
        user = None

    return Ok().as_response(data={
        'user': user,
        'messages_translate_pack': OK_BAD_MESSAGES_TRANSLATE_PACK,
        'app_version': APP_VERSION,
    })

# endregion
