__all__ = ('build_user_controllers',)

from fastapi import APIRouter
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto.requests import SignUpDto, UserPatchDto
from App.models.dto.responses import UserDto, ERROR_RESPONSES
from App.models.entities import RequestInfo
from App.models.dto.mapping import UserMapping
from App.services import UserService, AuthService


def build_user_controllers(inject: Deps):
    router = APIRouter(prefix="/users")

    @router.post("/new", response_model=UserDto, responses=ERROR_RESPONSES)
    async def ctrl(body: SignUpDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        user = await UserService(db, request).create_user(body)
        return await AuthService(db, request).authorize(user)

    @router.get("/me", response_model=UserDto, responses=ERROR_RESPONSES)
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        user = await UserService(db, request).get_user_by_id(request.user_id)
        return request.make_response(UserMapping.to_dto(user))

    @router.patch("/me", response_model=UserDto, responses=ERROR_RESPONSES)
    async def ctrl(body: UserPatchDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        user = await UserService(db, request).edit_user(request.user_id, body)
        return request.make_response(UserMapping.to_dto(user))

    return router
