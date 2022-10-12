from fastapi import FastAPI
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto import AppInfoDto
from App.models.entities import RequestInfo
from App.models.mapping import UserMapping
from App.services import UserService

__all__ = ('register_general_controllers', )

from App.settings import APP_VERSION, APP_ID
from App.special import Ok


def register_general_controllers(app: FastAPI, inject: Deps):

    @app.get("/info", response_model=AppInfoDto)
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        if request.session is not None:
            user = await UserService(db, request).get_user_by_id(request.user_id)
        else:
            user = None

        return request.make_response(Ok(), data={
            'app_id': APP_ID,
            'app_version': APP_VERSION,
            'user': UserMapping.to_dict(user) if user else None,
        })

    @app.get("/check")
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO_WS):

        return request.make_response(Ok())
