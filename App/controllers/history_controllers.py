from typing import List

from fastapi import FastAPI, Depends
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto import HistoryPageDto, HistoryKindDto, HistoryPageParamsDto
from App.models.entities import RequestInfo
from App.services import HistoryService
from App.special import Ok

__all__ = ('register_history_controllers', )


def register_history_controllers(app: FastAPI, inject: Deps):

    @app.get("/history/kinds", response_model=List[HistoryKindDto])
    def ctrl(request: RequestInfo = inject.REQUEST_INFO_WS):

        kinds = HistoryService.get_history_kinds(request)
        return request.make_response(Ok(), data=kinds)

    @app.get("/history", response_model=HistoryPageDto)
    async def ctrl(page: HistoryPageParamsDto = Depends(HistoryPageParamsDto),
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        page_result = await HistoryService(db).get_page(page, request)
        return request.make_response(Ok(), data=page_result)
