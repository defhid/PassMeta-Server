__all__ = ('register_user_controllers', )

from fastapi import FastAPI
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto.requests import SignUpDto, UserPatchDto
from App.models.dto.responses import ResultDto, UserDto, ERROR_RESPONSES
from App.models.entities import RequestInfo
from App.models.dto.mapping import UserMapping
from App.services import UserService, AuthService
from App.models.okbad import Ok


def register_user_controllers(app: FastAPI, inject: Deps):

    @app.post("/users/new", response_model=UserResultDto, responses=ERROR_RESPONSES)
    async def ctrl(body: SignUpDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        user = await UserService(db, request).create_user(body)
        return await AuthService(db, request).authorize(user)

    @app.get("/users/me", response_model=UserResultDto, responses=ERROR_RESPONSES)
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        user = await UserService(db, request).get_user_by_id(request.user_id)
        return request.make_response(Ok(), data=UserMapping.to_dict(user))

    @app.patch("/users/me", response_model=UserResultDto, responses=ERROR_RESPONSES)
    async def ctrl(body: UserPatchDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        user = await UserService(db, request).edit_user(request.user_id, body)
        return request.make_response(Ok(), data=UserMapping.to_dict(user))


class UserResultDto(ResultDto):
    data: UserDto
