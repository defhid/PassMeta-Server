from App.services.base import DbServiceBase
from App.services import AuthService

from App.models.db import User, PassFile, History
from App.models.request import PassfilePostData
from App.utils.passfile import PassFileUtils
from App.special import *

from sqlalchemy import select
from starlette.requests import Request
import datetime
import re

__all__ = (
    'PassFileService',
)


class PassFileService(DbServiceBase):
    __slots__ = ()

    async def get_user_passfiles(self, user: User) -> List[PassFile]:
        return list(await self.db.query(PassFile, select(PassFile).where(PassFile.user_id == user.id)))

    async def get_file(self, passfile_id: int, user: User, request: Request) -> (PassFile, bytes):
        """ Raises: Bad [NOT_EXIST_ERR, ACCESS_ERR].
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

        return passfile, await PassFileUtils.read_file(passfile)

    async def add_file(self, data: PassfilePostData, user: User, request: Request) -> PassFile:
        """ Auto-commit.
            Raises: Bad.
        """
        self._validate_data(data, True)

        passfile = PassFile(user_id=user.id, name=data.name, color=data.color, check_key=data.check_key)
        self.db.add(passfile)

        h = await self.history_writer.write(
            History.Kind.CREATE_PASSFILE_SUCCESS,
            user,
            more=f"pf:{passfile.id}",
            request=request,
            autocommit=True
        )

        if not await PassFileUtils.write_file(passfile, data.smth):
            await self.db.delete(passfile)
            await self.db.delete(h)
            await self.db.commit()
            raise Bad(None, UNKNOWN_ERR)

        return passfile

    async def edit_file(self, passfile_id: int, data: PassfilePostData, user: User, request: Request) -> PassFile:
        """ Auto-commit.
            Raises: Bad.
        """
        self._validate_data(data, False)

        passfile = await self.db.query_first(PassFile, select(PassFile).where(PassFile.id == passfile_id))
        if not passfile:
            raise Bad('passfile_id', NOT_EXIST_ERR)

        if passfile.user_id != user.id:
            await self.history_writer.write(
                History.Kind.EDIT_PASSFILE_FAILURE,
                user,
                more=f"ACCESS,pf:{passfile.id}",
                request=request
            )
            raise Bad(None, ACCESS_ERR)

        passfile.changed_on = datetime.datetime.utcnow()
        passfile.version += 1
        passfile.name = data.name
        passfile.color = data.color
        passfile.check_key = data.check_key

        await self.history_writer.write(
            History.Kind.EDIT_PASSFILE_SUCCESS,
            user,
            more=f"pf:{passfile.id}",
            request=request,
            autocommit=True
        )

        if not await PassFileUtils.write_file(passfile, data.smth):
            raise Bad(None, UNKNOWN_ERR)

        return passfile

    async def archive_file(self, passfile_id: int, user: User, request: Request):
        """ Auto-commit.
            Raises: Bad.
        """
        passfile = await self.db.query_first(PassFile, select(PassFile).where(PassFile.id == passfile_id))
        if not passfile:
            raise Bad('passfile_id', NOT_EXIST_ERR)

        if passfile.user_id != user.id:
            await self.history_writer.write(
                History.Kind.ARCHIVE_PASSFILE_FAILURE,
                user,
                more=f"ACCESS,pf:{passfile.id}",
                request=request
            )
            raise Bad(None, ACCESS_ERR)

        if passfile.is_archived:
            return Bad('passfile', NOT_AVAILABLE)

        passfile.is_archived = True

        if not PassFileUtils.archive_file(passfile):
            passfile.is_archived = False
            await self.history_writer.write(
                History.Kind.ARCHIVE_PASSFILE_SUCCESS,
                user,
                more=f"pf:{passfile.id}",
                request=request,
                autocommit=True
            )
            return

        await self.history_writer.write(
            History.Kind.ARCHIVE_PASSFILE_FAILURE,
            user,
            more=f"ERROR,pf:{passfile.id}",
            request=request,
            autocommit=True
        )

    async def unarchive_file(self, passfile_id: int, user: User, request: Request):
        """ Auto-commit.
            Raises: Bad.
        """
        passfile = await self.db.query_first(PassFile, select(PassFile).where(PassFile.id == passfile_id))
        if not passfile:
            raise Bad('passfile_id', NOT_EXIST_ERR)

        if passfile.user_id != user.id:
            await self.history_writer.write(
                History.Kind.UNARCHIVE_PASSFILE_FAILURE,
                user,
                more=f"ACCESS,pf:{passfile.id}",
                request=request
            )
            raise Bad(None, ACCESS_ERR)

        if not passfile.is_archived:
            return Bad('passfile', BAD_REQUEST_ERR, MORE.text("not archived"))

        if not PassFileUtils.unarchive_file(passfile):
            await self.history_writer.write(
                History.Kind.ARCHIVE_PASSFILE_SUCCESS,
                user,
                more=f"pf:{passfile.id}",
                request=request,
                autocommit=True
            )
            return

        passfile.is_archived = False

        await self.history_writer.write(
            History.Kind.ARCHIVE_PASSFILE_FAILURE,
            user,
            more=f"ERROR,pf:{passfile.id}",
            request=request,
            autocommit=True
        )

    async def delete_file(self, passfile_id: int, check_password: str, user: User, request: Request):
        """ Auto-commit.
            Raises: from get_file.
        """
        passfile = await self.db.query_first(PassFile, select(PassFile).where(PassFile.id == passfile_id))
        if not passfile:
            raise Bad('passfile_id', NOT_EXIST_ERR)

        if not AuthService.check_password(check_password, user):
            await self.history_writer.write(
                History.Kind.DELETE_PASSFILE_FAILURE,
                user,
                more=f"ACCESS,pf:{passfile.id}",
                request=request,
                autocommit=True
            )
            raise Bad("check_password", WRONG_VAL_ERR)

        if not PassFileUtils.delete_file(passfile):
            raise Bad(None, UNKNOWN_ERR)

        await self.db.delete(passfile)
        await self.history_writer.write(
            History.Kind.DELETE_PASSFILE_SUCCESS,
            user,
            more=f"pf:{passfile.id}",
            request=request,
            autocommit=True
        )

    @staticmethod
    def _validate_data(data: PassfilePostData, content_required: bool):
        if len(data.smth) < 1:
            raise Bad(None, DATA_ERR)

        if content_required and len(data.name) < 1:
            raise Bad('name', TOO_SHORT_ERR)

        if not data.color or len(data.color) != 6:
            data.color = None

        if data.color:
            data.color = data.color.lstrip("#").upper()
            if not re.fullmatch(re.compile("[0-9A-B]"), data.color):
                raise Bad('color', VAL_ERR)

        if data.check_key is None:
            raise Bad('check_key', VAL_MISSED_ERR)

        if len(data.check_key) != 128:
            raise Bad('check_key', VAL_ERR, MORE.text("incorrect length"))
