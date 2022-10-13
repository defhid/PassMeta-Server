from typing import List

from fastapi import FastAPI
from passql import DbConnection

from App.controllers.di import Deps
from App.models.dto import (
    PassFileDto, PassFileFullDto,
    PassfilePostDto,
    PassfileVersionDto, PassfileInfoDto,
    PassfileDeleteDto, PassFileVersionDto,
)
from App.models.entities import RequestInfo
from App.models.mapping import PassFileMapping, PassFileVersionMapping
from App.services import UserService, PassFileService
from App.settings import PASSFILES_ENCODING
from App.special import Ok

__all__ = ('register_passfile_controllers', )


def register_passfile_controllers(app: FastAPI, inject: Deps):

    @app.get("/passfiles", response_model=List[PassFileDto])
    async def ctrl(type_id: int = None,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()

        user = await UserService(db, request).get_user_by_id(request.user_id)
        passfiles = await PassFileService(db, request).get_user_passfiles(user, type_id)

        return request.make_response(Ok(), data=[PassFileMapping.to_dict(pf) for pf in passfiles])

    @app.get("/passfiles/{passfile_id}", response_model=PassFileFullDto)
    async def ctrl(passfile_id: int,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        passfile, data = await PassFileService(db, request).get_file(passfile_id, None)
        return request.make_response(Ok(), data=PassFileMapping.to_dict(passfile, data))

    @app.get("/passfiles/{passfile_id}/versions", response_model=PassFileVersionDto)
    async def ctrl(passfile_id: int,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        versions = await PassFileService(db, request).get_file_versions(passfile_id)
        return request.make_response(Ok(), data=[PassFileVersionMapping.to_dict(pfv) for pfv in versions])

    @app.get("/passfiles/{passfile_id}/versions/{version}", response_model=str)
    async def ctrl(passfile_id: int,
                   version: int,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        _, data = await PassFileService(db, request).get_file(passfile_id, version)
        return request.make_response(Ok(), data=data.decode(PASSFILES_ENCODING))

    @app.post("/passfiles/new", response_model=PassFileDto)
    async def ctrl(body: PassfilePostDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        passfile = await PassFileService(db, request).add_file(body)
        return request.make_response(Ok(), data=PassFileMapping.to_dict(passfile))

    @app.patch("/passfiles/{passfile_id}/info", response_model=PassFileDto)
    async def ctrl(passfile_id: int,
                   body: PassfileInfoDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        passfile = await PassFileService(db, request).edit_file_info(passfile_id, body)
        return request.make_response(Ok(), data=PassFileMapping.to_dict(passfile))

    @app.post("/passfiles/{passfile_id}/versions/new", response_model=PassFileDto)
    async def ctrl(passfile_id: int,
                   body: PassfileVersionDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        passfile = await PassFileService(db, request).edit_file_version(passfile_id, body)
        return request.make_response(Ok(), data=PassFileMapping.to_dict(passfile))

    @app.delete("/passfiles/{passfile_id}")
    async def ctrl(passfile_id: int,
                   body: PassfileDeleteDto,
                   request: RequestInfo = inject.REQUEST_INFO,
                   db: DbConnection = inject.DB):

        request.ensure_user_is_authorized()
        await PassFileService(db, request).delete_file(passfile_id, body.check_password)
        return request.make_response(Ok())
