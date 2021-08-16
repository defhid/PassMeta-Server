from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError

from App.models.request import *
from App.utils.db import *
from App.special import *
from App.settings import DEBUG

from App.services import (
    AuthService,
    UserService,
)

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
    async with db_async_engine.begin() as conn:
        await conn.run_sync(db_model_base.metadata.create_all)


# endregion


@app.post("/auth/sign-in")
async def sign_in(body: SignInPostData,
                  request: Request,
                  db_session: AsyncDbSession = Depends(db_session_getter)):

    service = AuthService(db_session)
    user = await service.authenticate(body, request)
    return await service.authorize(user, request)


@app.post("/auth/sign-out")
async def sign_out(request: Request,
                   db_session: AsyncDbSession = Depends(db_session_getter)):

    await AuthService(db_session).sign_out(request)
    return Ok().as_response()


@app.post("/auth/sign-up")
async def sign_up(body: SignUpPostData,
                  request: Request,
                  db_session: AsyncDbSession = Depends(db_session_getter)):

    user = await UserService(db_session).post(body)
    return await AuthService(db_session).authorize(user, request)


@app.get("/passfile")
async def passfile_get(request: Request,
                       db_session: AsyncDbSession = Depends(db_session_getter)):
    return {"message": "passfile get"}


@app.post("/passfile")
async def passfile_post(body: PassfilePostData,
                        request: Request,
                        db_session: AsyncDbSession = Depends(db_session_getter)):
    return {"message": "passfile post"}


@app.get("/users/me")
async def me_get(request: Request,
                 db_session: AsyncDbSession = Depends(db_session_getter)):

    user = await AuthService(db_session).get_user(request)
    return Ok().as_response(data=user.to_dict())


@app.patch("/users/me")
async def me_patch(body: UserSelfPatchData,
                   request: Request,
                   db_session: AsyncDbSession = Depends(db_session_getter)):
    return {"message": "passfile post"}
