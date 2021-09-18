from App.special import *
from App.models.request import *
from App.utils.db import DbUtils, AsyncDbSession
from App.utils.passfile import PassFileUtils
from App.utils.scheduler import Scheduler, SchedulerTask
from App.utils.session import SessionUtils
from App.utils.logging import Logger
from App.settings import *
from App.services import (
    AuthService,
    UserService,
    PassFileService,
)

from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError


logger = Logger(__file__)

db_utils = DbUtils()

scheduler = Scheduler(period_minutes=10)

app = FastAPI(debug=DEBUG)


# region Middlewares

@app.middleware('http')
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Result as e:
        return e.as_response()
    except Exception as e:
        logger.error("Request error", e, _need_trace=False)
        return Bad(None, SERVER_ERR, MORE.text(str(e)) if e.args else None).as_response()

# endregion


# region FastApi exception handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, ex: RequestValidationError):
    return Bad(None, BAD_REQUEST_ERR, MORE.info({"validation error": ex.errors()})).as_response()

# endregion


# region Event handlers

@app.on_event("startup")
async def on_startup():
    Logger.init('uvicorn.error' if __name__ == '__main__' else 'gunicorn.error')

    await db_utils.ensure_models_created()

    PassFileUtils.ensure_folders_created()

    scheduler.add(SchedulerTask(
        'SESCHECK',
        active=True,
        single=False,
        interval_minutes=OLD_SESSIONS_CHECKING_INTERVAL_MINUTES,
        start_now=OLD_SESSIONS_CHECKING_ON_STARTUP,
        func=SessionUtils.check_old_sessions
    ))

    scheduler.add(SchedulerTask(
        'APASCHECK',
        active=True,
        single=False,
        interval_minutes=OLD_PASSFILES_CHECKING_INTERVAL_MINUTES,
        start_now=OLD_PASSFILES_CHECKING_ON_STARTUP,
        func=PassFileUtils.check_archive_files
    ))

    scheduler.run()

# endregion


# region Aliases

GET = app.get
POST = app.post
PATCH = app.patch
PUT = app.put
DELETE = app.delete
DB = Depends(db_utils.session_maker)

# endregion


# region Auth

@POST("/auth/sign-in")
async def _(
        body: SignInPostData,
        request: Request,
        db_session: AsyncDbSession = DB
):
    service = AuthService(db_session)
    user = await service.authenticate(body, request)
    return await service.authorize(user, request)


@POST("/auth/sign-out")
async def _(
        request: Request,
        db_session: AsyncDbSession = DB
):
    await AuthService(db_session).sign_out(request)
    return Ok().as_response()

# endregion


# region Passfile

@GET("/passfiles/{passfile_id}")
async def _(
        passfile_id: int,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    passfile, data = await PassFileService(db_session).get_file(passfile_id, user, request)
    return Ok().as_response(data=passfile.to_dict(data))


@GET("/passfiles/list")
async def _(
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    passfiles = await PassFileService(db_session).get_user_passfiles(user)
    converted = list(map(lambda p: p.to_dict(), passfiles))
    return Ok().as_response(data=converted)


@POST("/passfiles/new")
async def _(
        body: PassfilePostData,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    passfile = await PassFileService(db_session).add_file(body, user, request)
    return Ok().as_response(data=passfile.to_dict())


@PATCH("/passfiles/{passfile_id}")
async def _(
        passfile_id: int,
        body: PassfilePostData,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    await PassFileService(db_session).edit_file(passfile_id, body, user, request)
    return Ok().as_response()


@PUT("/passfiles/{passfile_id}/to/archive")
async def _(
        passfile_id: int,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    await PassFileService(db_session).archive_file(passfile_id, user, request)
    return Ok().as_response()


@PUT("/passfiles/{passfile_id}/to/actual")
async def _(
        passfile_id: int,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    await PassFileService(db_session).unarchive_file(passfile_id, user, request)
    return Ok().as_response()


@DELETE("/passfiles/{passfile_id}")
async def _(
        passfile_id: int,
        check_password: str,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    await PassFileService(db_session).delete_file(passfile_id, check_password, user, request)
    return Ok().as_response()

# endregion


# region Users

@POST("/users/new")
async def _(
        body: SignUpPostData,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await UserService(db_session).create_user(body, request)
    return await AuthService(db_session).authorize(user, request)


@GET("/users/me")
async def _(
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    return Ok().as_response(data=user.to_dict())


@PATCH("/users/me")
async def _(
        body: UserPatchData,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    user = await UserService(db_session).edit_user(user.id, body, user, request)
    return Ok().as_response(data=user.to_dict())

# endregion


# region info

@GET("/info")
async def _(
        request: Request,
        db_session: AsyncDbSession = DB
):
    try:
        user = await AuthService(db_session).get_user(request)
    except Bad:
        user = None

    return Ok().as_response(data={
        'user': user.to_dict() if user else None,
        'messages_translate_pack': OK_BAD_MESSAGES_TRANSLATE_PACK,
        'app_version': APP_VERSION,
    })

# endregion
