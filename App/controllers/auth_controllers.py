from fastapi import FastAPI
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto import SignInDto
from App.models.entities import RequestInfo
from App.services import AuthService

__all__ = ('register_auth_controllers', )


def register_auth_controllers(app: FastAPI, inject: Deps):

    @app.post("/auth/sign-in")
    async def ctrl(body: SignInDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        service = AuthService(db)
        user = await service.authenticate(body, request)
        return await service.authorize(user, request)

    @app.post("/auth/reset/all")
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        return await AuthService(db).reset(request, False)

    @app.post("/auth/reset/all-except-me")
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        return await AuthService(db).reset(request, True)
