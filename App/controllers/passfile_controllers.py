__all__ = ('register_passfile_controllers', )

from fastapi import FastAPI, File, Depends
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto.requests import PassfilePostDto, PassfilePatchDto, PassfileListParamsDto
from App.models.dto.responses import PassfileDto, PassfileListDto, PassfileVersionListDto, ERROR_RESPONSES
from App.models.entities import RequestInfo
from App.models.dto.mapping import PassFileMapping, PassFileVersionMapping
from App.services import UserService, PassFileService


def register_passfile_controllers(app: FastAPI, inject: Deps):

    @app.get("/passfiles", response_model=PassfileListDto, responses=ERROR_RESPONSES)
    async def ctrl(page: PassfileListParamsDto = Depends(PassfileListParamsDto),
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()

        user = await UserService(db, request).get_user_by_id(request.user_id)
        passfiles = await PassFileService(db, request).get_user_passfiles(user, page)

        return request.make_response(PassfileListDto.model_construct(
            list=[PassFileMapping.to_dto(pf) for pf in passfiles]
        ))

    @app.get("/passfiles/{passfile_id}", response_model=PassfileDto, responses=ERROR_RESPONSES)
    async def ctrl(passfile_id: int,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        passfile = await PassFileService(db, request).get_passfile(passfile_id)
        return request.make_response(PassFileMapping.to_dto(passfile))

    @app.get("/passfiles/{passfile_id}/versions", response_model=PassfileVersionListDto, responses=ERROR_RESPONSES)
    async def ctrl(passfile_id: int,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        versions = await PassFileService(db, request).get_passfile_versions(passfile_id)
        return request.make_response(PassfileVersionListDto.model_construct(
            list=[PassFileVersionMapping.to_dto(pfv) for pfv in versions]
        ))

    @app.get("/passfiles/{passfile_id}/versions/{version}", response_model=bytes, responses=ERROR_RESPONSES)
    async def ctrl(passfile_id: int,
                   version: int,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        data = await PassFileService(db, request).get_passfile_smth(passfile_id, version)
        return request.make_bytes_response(data)

    @app.post("/passfiles/new", response_model=PassfileDto, responses=ERROR_RESPONSES)
    async def ctrl(body: PassfilePostDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        passfile = await PassFileService(db, request).add_passfile(body)
        return request.make_response(PassFileMapping.to_dto(passfile))

    @app.patch("/passfiles/{passfile_id}", response_model=PassfileDto, responses=ERROR_RESPONSES)
    async def ctrl(passfile_id: int,
                   body: PassfilePatchDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        passfile = await PassFileService(db, request).edit_passfile_info(passfile_id, body)
        return request.make_response(PassFileMapping.to_dto(passfile))

    @app.post("/passfiles/{passfile_id}/versions/new", response_model=PassfileDto, responses=ERROR_RESPONSES)
    async def ctrl(passfile_id: int,
                   smth: bytes = File(),
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        passfile = await PassFileService(db, request).edit_passfile_smth(passfile_id, smth)
        return request.make_response(PassFileMapping.to_dto(passfile))

    @app.delete("/passfiles/{passfile_id}", responses=ERROR_RESPONSES)
    async def ctrl(passfile_id: int,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        await PassFileService(db, request).delete_passfile(passfile_id)
        return request.make_response()

