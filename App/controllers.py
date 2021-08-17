from App.models.request import *
from App.utils.db import *
from App.utils.passfile import PassFileUtils
from App.special import *
from App.settings import DEBUG
from App.services import (
    AuthService,
    UserService,
    PassFileService,
)

from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError

app = FastAPI(debug=DEBUG)

# region exception handlers


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, ex: RequestValidationError):
    return Bad(None, BAD_REQUEST_ERR, MORE.info({"validation error": ex.errors()})).as_response()


@app.exception_handler(Result)
async def validation_exception_handler(_: Request, ex: Result):
    return ex.as_response()


@app.exception_handler(Exception)
async def validation_exception_handler(_: Request, ex: Exception):
    return Bad(None, SERVER_ERR, MORE.text(str(ex))).as_response()


# endregion


# region event handlers


@app.on_event("startup")
async def on_startup():
    await DbUtils.ensure_models_created()
    PassFileUtils.ensure_folders_created()


# endregion


DB_SESSION_GETTER = Depends(DbUtils.session_getter)


@app.post("/auth/sign-in")
async def sign_in(body: SignInPostData,
                  request: Request,
                  db_session: AsyncDbSession = DB_SESSION_GETTER):

    service = AuthService(db_session)
    user = await service.authenticate(body, request)
    return await service.authorize(user, request)


@app.post("/auth/sign-out")
async def sign_out(request: Request,
                   db_session: AsyncDbSession = DB_SESSION_GETTER):

    await AuthService(db_session).sign_out(request)
    return Ok().as_response()


@app.get("/passfile/{passfile_id}")
async def passfile_get(passfile_id: int,
                       request: Request,
                       db_session: AsyncDbSession = DB_SESSION_GETTER):

    user = await AuthService(db_session).get_user(request)
    passfile = await PassFileService(db_session).get_file(passfile_id, user, request)
    return Ok().as_response(data=passfile.to_dict())


@app.post("/passfile")
async def passfile_post(body: PassfilePostData,
                        request: Request,
                        db_session: AsyncDbSession = DB_SESSION_GETTER):

    user = await AuthService(db_session).get_user(request)
    passfile = await PassFileService(db_session).save_file(body, user, request)
    return Ok().as_response(data=passfile.to_dict())


@app.post("/passfile/{passfile_id}")
async def passfile_delete(passfile_id: int,
                          request: Request,
                          db_session: AsyncDbSession = DB_SESSION_GETTER):

    user = await AuthService(db_session).get_user(request)
    await PassFileService(db_session).delete_file(passfile_id, user, request)
    return Ok().as_response()


@app.post("/users/new")
async def user_new_post(body: SignUpPostData,
                        request: Request,
                        db_session: AsyncDbSession = DB_SESSION_GETTER):

    user = await UserService(db_session).create_user(body, request)
    return await AuthService(db_session).authorize(user, request)


@app.get("/users/me")
async def user_me_get(request: Request,
                      db_session: AsyncDbSession = DB_SESSION_GETTER):

    user = await AuthService(db_session).get_user(request)
    return Ok().as_response(data=user.to_dict())


@app.patch("/users/me")
async def user_me_patch(body: UserPatchData,
                        request: Request,
                        db_session: AsyncDbSession = DB_SESSION_GETTER):

    user = await AuthService(db_session).get_user(request)
    user = await UserService(db_session).edit_user(user.id, body, user, request)
    return Ok().as_response(data=user.to_dict())
