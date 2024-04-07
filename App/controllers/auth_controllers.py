__all__ = ('build_auth_controllers',)

from fastapi import APIRouter
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto.requests import SignInDto
from App.models.dto.responses import UserDto, ERROR_RESPONSES
from App.models.entities import RequestInfo
from App.services import AuthService


def build_auth_controllers(inject: Deps):
    router = APIRouter()

    @router.post("/auth/sign-in", response_model=UserDto, responses=ERROR_RESPONSES)
    async def ctrl(body: SignInDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        service = AuthService(db, request)
        user = await service.authenticate(body)
        return await service.authorize(user)

    @router.post("/auth/reset/me", responses=ERROR_RESPONSES)
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO):

        return AuthService.reset(request)

    @router.post("/auth/reset/all", responses=ERROR_RESPONSES)
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        return await AuthService(db, request).reset_all(request, False)

    @router.post("/auth/reset/all-except-me", responses=ERROR_RESPONSES)
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        return await AuthService(db, request).reset_all(request, True)

    return router
