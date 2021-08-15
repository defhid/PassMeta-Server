from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError
from starlette.responses import Response
from App.models.request import *
from App.utils.db import *
from App.special import *

app = FastAPI(debug=True)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, err: RequestValidationError):
    return Response(
        Bad(None, BAD_REQUEST_ERR, MORE.info({"validation error": err.errors()})).dict(),
        status_code=BAD_REQUEST_ERR.response_status_code
    )


@app.exception_handler(Result)
async def validation_exception_handler(_: Request, res: Result):
    return Response(res.dict(), status_code=res.message.response_status_code)


@app.post("/auth/sign-in")
async def sign_in(body: SignInPostData,
                  request: Request,
                  db_session: AsyncSession = Depends(db_session_getter)):
    return {"message": "sign in"}


@app.post("/auth/sign-out")
async def sign_out(request: Request,
                   db_session: AsyncSession = Depends(db_session_getter)):
    return {"message": "sign out"}


@app.post("/auth/sign-up")
async def sign_up(body: SignUpPostData,
                  request: Request,
                  db_session: AsyncSession = Depends(db_session_getter)):
    return {"message": "sign up"}


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
    return {"message": "passfile post"}


@app.patch("/users/me")
async def me_patch(body: UserSelfPatchData,
                   request: Request,
                   db_session: AsyncSession = Depends(db_session_getter)):
    return {"message": "passfile post"}
