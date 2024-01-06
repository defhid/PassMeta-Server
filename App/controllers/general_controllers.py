__all__ = ('register_general_controllers', )

from fastapi import FastAPI
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto.responses import ResultDto, AppInfoDto, ERROR_RESPONSES
from App.models.entities import RequestInfo
from App.models.dto.mapping import UserMapping
from App.services import UserService
from App.settings import APP_VERSION, APP_ID


def register_general_controllers(app: FastAPI, inject: Deps):

    @app.get("/info", response_model=AppInfoDto, responses=ERROR_RESPONSES)
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        if request.session is not None:
            user = await UserService(db, request).get_user_by_id(request.user_id)
        else:
            user = None

        return request.make_response(AppInfoDto.model_construct(
            app_id=APP_ID,
            app_version=APP_VERSION,
            user=UserMapping.to_dto(user) if user else None,
        ))

    @app.get("/check")
    async def ctrl(request: RequestInfo = inject.REQUEST_INFO_WS):

        return request.make_response()
