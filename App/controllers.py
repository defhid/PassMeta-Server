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


DB = Depends(db_utils.session_maker)


# region Auth

@app.post("/auth/sign-in")
async def controller(
        body: SignInPostData,
        request: Request,
        db_session: AsyncDbSession = DB
):
    service = AuthService(db_session)
    user = await service.authenticate(body, request)
    return await service.authorize(user, request)


@app.post("/auth/sign-out")
async def controller(
        request: Request,
        db_session: AsyncDbSession = DB
):
    await AuthService(db_session).sign_out(request)
    return Ok().as_response()

# endregion


# region Passfile

@app.get("/passfiles/{passfile_id}")
async def controller(
        passfile_id: int,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    passfile, data = await PassFileService(db_session).get_file(passfile_id, user, request)
    return Ok().as_response(data=passfile.to_dict(data))


@app.post("/passfiles/new")
async def controller(
        body: PassfilePostData,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    passfile = await PassFileService(db_session).save_file(body, user, request)
    return Ok().as_response(data=passfile.to_dict())


@app.post("/passfiles/{passfile_id}")
async def controller(
        passfile_id: int,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    await PassFileService(db_session).delete_file(passfile_id, user, request)
    return Ok().as_response()

# endregion


# region Users

@app.post("/users/new")
async def controller(
        body: SignUpPostData,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await UserService(db_session).create_user(body, request)
    return await AuthService(db_session).authorize(user, request)


@app.get("/users/me")
async def controller(
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    return Ok().as_response(data=user.to_dict())


@app.patch("/users/me")
async def controller(
        body: UserPatchData,
        request: Request,
        db_session: AsyncDbSession = DB
):
    user = await AuthService(db_session).get_user(request)
    user = await UserService(db_session).edit_user(user.id, body, user, request)
    return Ok().as_response(data=user.to_dict())

# endregion


# region info

@app.get("/info")
async def controller(
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
