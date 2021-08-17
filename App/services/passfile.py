from App.services.base import DbServiceBase
from App.models.db import User, PassFile, History
from App.models.request import PassfilePostData
from App.utils.passfile import PassFileUtils
from App.special import *

from sqlalchemy import select
from starlette.requests import Request

import os
import datetime

__all__ = (
    'PassFileService',
)


class PassFileService(DbServiceBase):
    __slots__ = ()

    async def get_file(self, passfile_id: int, user: User, request: Request) -> PassFile:
        """ Raises: NOT_EXIST_ERR, ACCESS_ERR.
        """
        passfile = await self.db.query_first(PassFile, select(PassFile).where(PassFile.id == passfile_id))
        if not passfile:
            raise Bad('passfile_id', NOT_EXIST_ERR)

        if passfile.user_id != user.id:
            await self.history_writer.write(
                History.Kind.GET_PASSFILE_FAILURE,
                user,
                more=f"ACCESS,pf:{passfile.id}",
                request=request
            )
            raise Bad('passfile_id', ACCESS_ERR)

        await self.history_writer.write(
            History.Kind.GET_PASSFILE_SUCCESS,
            user,
            more=f"pf:{passfile.id}",
            request=request
        )

        passfile.data = await PassFileUtils.read_file(passfile.path)
        return passfile

    async def save_file(self, data: PassfilePostData, user: User, request: Request) -> PassFile:
        """ Auto-commit.
            Raises: DATA_ERR, NOT_EXIST_ERR, ACCESS_ERR.
        """
        if len(data.smth) < 1:
            raise Bad(None, DATA_ERR)

        if data.passfile_id:
            passfile = await self.db.query_first(PassFile, select(PassFile).where(PassFile.id == data.passfile_id))
            if not passfile:
                raise Bad('passfile_id', NOT_EXIST_ERR)

            if passfile.user_id != user.id:
                await self.history_writer.write(
                    History.Kind.SET_PASSFILE_FAILURE,
                    user,
                    more=f"ACCESS,pf:{passfile.id}",
                    request=request
                )
                raise Bad(None, ACCESS_ERR)

            passfile.changed_on = datetime.datetime.utcnow()
        else:
            passfile = PassFile(user_id=user.id)
            self.db.add(passfile)

        await PassFileUtils.write_file(data.smth, passfile.path)

        await self.history_writer.write(  # autocommit
            History.Kind.SET_PASSFILE_SUCCESS,
            user,
            more=f"pf:{passfile.id}",
            request=request
        )
        return passfile

    async def delete_file(self, passfile_id: int, user: User, request: Request):
        """ Auto-commit.
            Raises: from get_file.
        """
        passfile = await self.db.query_first(PassFile, select(PassFile).where(PassFile.id == passfile_id))
        if not passfile:
            raise Bad('passfile_id', NOT_EXIST_ERR)

        if passfile.user_id != user.id:
            await self.history_writer.write(
                History.Kind.DELETE_PASSFILE_FAILURE,
                user,
                more=f"ACCESS,pf:{passfile.id}",
                request=request
            )
            raise Bad(None, ACCESS_ERR)

        await self.db.delete(passfile)
        await self.history_writer.write(  # autocommit
            History.Kind.DELETE_PASSFILE_SUCCESS,
            user,
            more=f"pf:{passfile.id}",
            request=request
        )

        filepath = passfile.path
        filepath_archive = passfile.archive_path

        if filepath != filepath_archive:
            try:
                if os.path.exists(filepath):
                    os.replace(filepath, filepath_archive)
            except Exception as e:
                pass
                # TODO: log critical
