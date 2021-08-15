from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from App.models.request import *
from App.utils.db import *
from App.special import *
from App.settings import DEBUG

from App.services.auth import AuthService
from App.services.users import UserService

app = FastAPI(debug=DEBUG)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, err: RequestValidationError):
    return JSONResponse(
        Bad(None, BAD_REQUEST_ERR, MORE.info({"validation error": err.errors()})).dict(),
        status_code=BAD_REQUEST_ERR.response_status_code
    )


@app.exception_handler(Result)
async def validation_exception_handler(_: Request, res: Result):
    return JSONResponse(
        res.dict(),
        status_code=res.message.response_status_code
    )


@app.exception_handler(Exception)
async def validation_exception_handler(_: Request, ex: Exception):
    return JSONResponse(
        Bad(None, SERVER_ERR, MORE.text(str(ex))).dict(),
        status_code=SERVER_ERR.response_status_code
    )


@app.on_event("startup")
async def on_startup():
    async with db_async_engine.begin() as conn:
        await conn.run_sync(db_model_base.metadata.create_all)


@app.post("/auth/sign-in")
async def sign_in(body: SignInPostData,
                  request: Request,
                  db_session: AsyncSession = Depends(db_session_getter)):

    user = await AuthService.authenticate(body, db_session)
    return await AuthService.authorize(user, request, db_session)


@app.post("/auth/sign-out")
async def sign_out(request: Request,
                   db_session: AsyncSession = Depends(db_session_getter)):

    await AuthService.sign_out(request, db_session)
    return Ok().dict()


@app.post("/auth/sign-up")
async def sign_up(body: SignUpPostData,
                  request: Request,
                  db_session: AsyncSession = Depends(db_session_getter)):

    user = await UserService.post(body, db_session)
    return await AuthService.authorize(user, request, db_session)


@app.get("/passfile")
async def passfile_get(request: Request,
                       db_session: AsyncSession = Depends(db_session_getter)):
    return {"message": "passfile get"}


@app.post("/passfile")
async def passfile_post(body: PassfilePostData,
                        request: Request,
                        db_session: AsyncSession = Depends(db_session_getter)):
    return {"message": "passfile post"}


@app.get("/users/me")
async def me_get(request: Request,
                 db_session: AsyncSession = Depends(db_session_getter)):

    user = await AuthService.get_user_async(request, db_session)
    return Ok(data=user).dict()


@app.patch("/users/me")
async def me_patch(body: UserSelfPatchData,
                   request: Request,
                   db_session: AsyncSession = Depends(db_session_getter)):
    return {"message": "passfile post"}
