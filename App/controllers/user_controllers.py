from fastapi import FastAPI
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto import SignUpDto, UserPatchDto, UserDto
from App.models.entities import RequestInfo
from App.models.mapping import UserMapping
from App.services import UserService, AuthService
from App.special import Ok

__all__ = ('register_user_controllers', )


def register_user_controllers(app: FastAPI, inject: Deps):

    @app.post("/users/new")
    async def ctrl(body: SignUpDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        user = await UserService(db, request).create_user(body)
        return await AuthService(db, request).authorize(user)

    @app.get("/users/me", response_model=UserDto)
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        user = await UserService(db, request).get_user_by_id(request.user_id)
        return request.make_response(Ok(), data=UserMapping.to_dict(user))

    @app.patch("/users/me", response_model=UserDto)
    async def ctrl(body: UserPatchDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        user = await UserService(db, request).edit_user(request.user_id, body)
        return request.make_response(Ok(), data=UserMapping.to_dict(user))
