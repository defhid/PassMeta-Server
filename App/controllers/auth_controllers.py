__all__ = ('register_auth_controllers', )

from fastapi import FastAPI
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto.requests import SignInDto
from App.models.dto.responses import ResultDto, UserDto, ERROR_RESPONSES
from App.models.entities import RequestInfo
from App.services import AuthService


def register_auth_controllers(app: FastAPI, inject: Deps):

    @app.post("/auth/sign-in", response_model=UserResultDto, responses=ERROR_RESPONSES)
    async def ctrl(body: SignInDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        service = AuthService(db, request)
        user = await service.authenticate(body)
        return await service.authorize(user)

    @app.post("/auth/reset/all", response_model=ResultDto, responses=ERROR_RESPONSES)
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        return await AuthService(db, request).reset(request, False)

    @app.post("/auth/reset/all-except-me", response_model=ResultDto, responses=ERROR_RESPONSES)
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        return await AuthService(db, request).reset(request, True)


class UserResultDto(ResultDto):
    data: UserDto
