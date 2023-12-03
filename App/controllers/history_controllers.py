__all__ = ('register_history_controllers', )

from fastapi import FastAPI, Depends
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto.requests import HistoryPageParamsDto
from App.models.dto.responses import HistoryPageDto, HistoryKindListDto, ERROR_RESPONSES
from App.models.entities import RequestInfo
from App.services import HistoryService


def register_history_controllers(app: FastAPI, inject: Deps):

    @app.get("/history/kinds", response_model=HistoryKindListDto, responses=ERROR_RESPONSES)
    def ctrl(request: RequestInfo = inject.REQUEST_INFO_WS):

        kinds = HistoryService.get_history_kinds(request)
        return request.make_response(HistoryKindListDto.model_construct(list=kinds))

    @app.get("/history/pages/{page_index}", response_model=HistoryPageDto, responses=ERROR_RESPONSES)
    async def ctrl(page: HistoryPageParamsDto = Depends(HistoryPageParamsDto),
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        page_result = await HistoryService(db, request).get_page(page)
        return request.make_response(page_result)

