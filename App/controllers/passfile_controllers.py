from typing import List

from fastapi import FastAPI
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto import (
    PassFileDto, PassFileFullDto,
    PassfileNewDto,
    PassfileSmthPatchDto, PassfileInfoPatchDto,
    PassfileDeleteDto,
)
from App.models.entities import RequestInfo
from App.models.mapping import PassFileMapping
from App.services import UserService, PassFileService
from App.settings import PASSFILES_ENCODING
from App.special import Ok

__all__ = ('register_passfile_controllers', )


def register_passfile_controllers(app: FastAPI, inject: Deps):

    @app.get("/passfiles/list", response_model=List[PassFileDto])
    async def ctrl(type_id: int = None,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()

        user = await UserService(db).get_user_by_id(request.user_id)
        passfiles = await PassFileService(db).get_user_passfiles(user, type_id)

        return request.make_response(Ok(), data=[PassFileMapping.to_dict(pf) for pf in passfiles])

    @app.get("/passfiles/{passfile_id}", response_model=PassFileFullDto)
    async def ctrl(passfile_id: int,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        passfile, data = await PassFileService(db).get_file(passfile_id, None, request)
        return request.make_response(Ok(), data=PassFileMapping.to_dict(passfile, data))

    @app.get("/passfiles/{passfile_id}/smth", response_model=str)
    async def ctrl(passfile_id: int,
                   version: int = None,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        _, data = await PassFileService(db).get_file(passfile_id, version, request)
        return request.make_response(Ok(), data=data.decode(PASSFILES_ENCODING))

    @app.post("/passfiles/new", response_model=PassFileDto)
    async def ctrl(body: PassfileNewDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        passfile = await PassFileService(db).add_file(body, request)
        return request.make_response(Ok(), data=PassFileMapping.to_dict(passfile))

    @app.patch("/passfiles/{passfile_id}/info", response_model=PassFileDto)
    async def ctrl(passfile_id: int,
                   body: PassfileInfoPatchDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        passfile = await PassFileService(db).edit_file_info(passfile_id, body, request)
        return request.make_response(Ok(), data=PassFileMapping.to_dict(passfile))

    @app.patch("/passfiles/{passfile_id}/smth", response_model=PassFileDto)
    async def ctrl(passfile_id: int,
                   body: PassfileSmthPatchDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        passfile = await PassFileService(db).edit_file_smth(passfile_id, body, request)
        return request.make_response(Ok(), data=PassFileMapping.to_dict(passfile))

    @app.delete("/passfiles/{passfile_id}")
    async def ctrl(passfile_id: int,
                   body: PassfileDeleteDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        await PassFileService(db).delete_file(passfile_id, body.check_password, request)
        return request.make_response(Ok())
