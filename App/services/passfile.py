from App.services.base import DbServiceBase
from App.services import AuthService
from App.settings import ARCHIVED_PASSFILE_LIFETIME_DAYS
from App.special import *

from App.models.db import User, PassFile, History
from App.models.request import PassfilePostData, PassfileInfoPatchData, PassfileSmthPatchData
from App.models.entities import RequestInfo

from App.utils.db import MakeSql
from App.utils.passfile import PassFileUtils
from App.utils.scheduler import SchedulerTask

import datetime
import re

__all__ = (
    'PassFileService',
)


class PassFileService(DbServiceBase):
    __slots__ = ()

    async def get_user_passfiles(self, user: User) -> List[PassFile]:
        return await self.db.query_list(PassFile, self._SELECT_BY_USER_ID, {'user_id': user.id})

    async def get_file(self, passfile_id: int, request: RequestInfo) -> (PassFile, bytes):
        """ Raises: Bad [NOT_EXIST_ERR, ACCESS_ERR].
        """
        passfile = await self._get_passfile_or_raise(passfile_id)

        if passfile.user_id != request.user_id:
            await self.history_writer.write(History.Kind.GET_PASSFILE_FAILURE,
                                            request.user_id, passfile.user_id,
                                            more=f"ACCESS,pf:{passfile.id}", request=request)
            raise Bad('passfile_id', ACCESS_ERR)

        await self.history_writer.write(History.Kind.GET_PASSFILE_SUCCESS,
                                        request.user_id, passfile.user_id,
                                        more=f"pf:{passfile.id}", request=request)

        return passfile, await PassFileUtils.read_file(passfile)

    async def add_file(self, data: PassfilePostData, request: RequestInfo) -> PassFile:
        """ Raises: Bad.
        """
        self._validate_post_data(data)

        result, passfile = None, None
        transaction = self.db.transaction()
        try:
            await transaction.start()
            passfile = await self.db.query_first(PassFile, self._INSERT, {
                'user_id': request.user_id,
                'name': data.name,
                'color': data.color,
                'check_key': data.check_key,
            })

            result = await PassFileUtils.write_file(passfile, data.smth)
            result.raise_if_failure()

            await self.history_writer.write(History.Kind.CREATE_PASSFILE_SUCCESS,
                                            request.user_id, passfile.user_id,
                                            more=f"pf:{passfile.id}", request=request)
        except BaseException:
            await transaction.rollback()
            if result:
                PassFileUtils.delete_file(passfile)
            raise
        else:
            await transaction.commit()

        return passfile

    async def edit_file_info(self, passfile_id: int,
                             data: PassfileInfoPatchData, request: RequestInfo) -> PassFile:
        """ Raises: Bad.
        """
        self._validate_info(data)

        passfile = await self._get_passfile_or_raise(passfile_id)

        if passfile.user_id != request.user_id:
            await self.history_writer.write(History.Kind.EDIT_PASSFILE_INFO_FAILURE,
                                            request.user_id, passfile.user_id,
                                            more=f"ACCESS,pf:{passfile.id}", request=request)
            raise Bad(None, ACCESS_ERR)

        passfile.name = data.name
        passfile.color = data.color

        async with self.db.transaction():
            passfile = await self.db.query_first(PassFile, self._UPDATE_INFO, passfile)

            await self.history_writer.write(History.Kind.EDIT_PASSFILE_INFO_SUCCESS,
                                            request.user_id, passfile.id,
                                            more=f"pf:{passfile.id}", request=request)
        return passfile

    async def edit_file_smth(self, passfile_id: int,
                             data: PassfileSmthPatchData, request: RequestInfo) -> PassFile:
        """ Raises: Bad.
        """
        self._validate_smth(data)

        passfile = await self._get_passfile_or_raise(passfile_id)

        if passfile.user_id != request.user_id:
            await self.history_writer.write(History.Kind.EDIT_PASSFILE_SMTH_FAILURE,
                                            request.user_id, passfile.user_id,
                                            more=f"ACCESS,pf:{passfile.id}", request=request)
            raise Bad(None, ACCESS_ERR)

        if passfile.is_archived:
            raise Bad('passfile', INVALID_OPERATION_ERR, MORE.text("ARCHIVED"))

        passfile.version += 1
        passfile.check_key = data.check_key

        result = await PassFileUtils.write_file(passfile, data.smth)
        result.raise_if_failure()

        transaction = self.db.transaction()
        try:
            await transaction.start()
            passfile = await self.db.query_first(PassFile, self._UPDATE_SMTH, passfile)

            await self.history_writer.write(History.Kind.EDIT_PASSFILE_SMTH_SUCCESS,
                                            request.user_id, passfile.user_id,
                                            more=f"pf:{passfile.id}", request=request)
        except Exception:
            await transaction.rollback()
            PassFileUtils.delete_file(passfile)
            raise
        else:
            await transaction.commit()
            PassFileUtils.optimize_file_versions(passfile)

        return passfile

    async def archive_file(self, passfile_id: int, request: RequestInfo) -> PassFile:
        """ Raises: Bad.
        """
        passfile = await self._get_passfile_or_raise(passfile_id)

        if passfile.user_id != request.user_id:
            await self.history_writer.write(History.Kind.ARCHIVE_PASSFILE_FAILURE,
                                            request.user_id, passfile.user_id,
                                            more=f"ACCESS,pf:{passfile.id}", request=request)
            raise Bad(None, ACCESS_ERR)

        if passfile.is_archived:
            raise Bad('passfile', INVALID_OPERATION_ERR, MORE.text("ARCHIVED"))

        async with self.db.transaction():
            passfile = await self.db.query_first(PassFile, self._ARCHIVE, passfile)

            await self.history_writer.write(History.Kind.ARCHIVE_PASSFILE_SUCCESS,
                                            request.user_id, passfile.user_id,
                                            more=f"pf:{passfile.id}", request=request)

        PassFileUtils.archive_file(passfile)
        return passfile

    async def unarchive_file(self, passfile_id: int, request: RequestInfo) -> PassFile:
        """ Raises: Bad.
        """
        passfile = await self._get_passfile_or_raise(passfile_id)

        if passfile.user_id != request.user_id:
            await self.history_writer.write(History.Kind.UNARCHIVE_PASSFILE_FAILURE,
                                            request.user_id, passfile.user_id,
                                            more=f"ACCESS,pf:{passfile.id}", request=request)
            raise Bad(None, ACCESS_ERR)

        if not passfile.is_archived:
            raise Bad('passfile', INVALID_OPERATION_ERR, MORE.text("NOT ARCHIVED"))

        result = None
        transaction = self.db.transaction()
        try:
            await transaction.start()
            passfile = await self.db.query_first(PassFile, self._UNARCHIVE, passfile)

            result = PassFileUtils.unarchive_file(passfile)
            result.raise_if_failure()

            await self.history_writer.write(History.Kind.UNARCHIVE_PASSFILE_SUCCESS,
                                            request.user_id, passfile.user_id,
                                            more=f"pf:{passfile.id}", request=request)
        except BaseException:
            await transaction.rollback()
            if result:
                PassFileUtils.archive_file(passfile)
            raise
        else:
            await transaction.commit()

        return passfile

    async def delete_file(self, passfile_id: int, check_password: str, request: RequestInfo):
        """ Raises: Bad.
        """
        passfile = await self._get_passfile_or_raise(passfile_id)

        if not passfile.is_archived:
            raise Bad('passfile', INVALID_OPERATION_ERR, MORE.text("NOT ARCHIVED"))

        user = await request.session.get_user(self.db)

        if not AuthService.check_password(check_password, user.pwd):
            await self.history_writer.write(History.Kind.DELETE_PASSFILE_FAILURE,
                                            request.user_id, passfile.user_id,
                                            more=f"ACCESS,pf:{passfile.id}", request=request)
            raise Bad("check_password", WRONG_VAL_ERR)

        async with self.db.transaction():
            await self.db.execute(self._DELETE, passfile)

            await self.history_writer.write(History.Kind.DELETE_PASSFILE_SUCCESS,
                                            request.user_id, passfile.user_id,
                                            more=f"pf:{passfile.id}", request=request)

        PassFileUtils.delete_file(passfile)

    async def _get_passfile_or_raise(self, passfile_id: int) -> PassFile:
        passfile = await self.db.query_first(PassFile, self._SELECT_BY_ID, {'id': passfile_id})
        if passfile is None:
            raise Bad('passfile_id', NOT_EXIST_ERR)

        return passfile

    @classmethod
    def _validate_post_data(cls, data: PassfilePostData):
        cls._validate_info(data)
        cls._validate_smth(data)

    @staticmethod
    def _validate_info(data):
        errors = []
        c = PassFile.Constrains

        if not data.name:
            errors.append(Bad('name', VAL_MISSED_ERR))

        data.name = data.name.strip()
        if len(data.name) < c.NAME_LEN_MIN:
            errors.append(Bad('name', TOO_SHORT_ERR, MORE.min_allowed(c.NAME_LEN_MIN)))
        elif len(data.name) > c.NAME_LEN_MAX:
            errors.append(Bad('name', TOO_LONG_ERR, MORE.max_allowed(c.NAME_LEN_MAX)))

        if not data.color:
            data.color = None
        else:
            data.color = data.color.lstrip("#").upper()
            if not re.fullmatch(re.compile("^[0-9A-F]{6}$"), data.color):
                errors.append(Bad('color', VAL_ERR, MORE.allowed("HEX")))

        if errors:
            raise Bad(None, DATA_ERR, sub=errors)

    @staticmethod
    def _validate_smth(data):
        if data.check_key is None:
            raise Bad('check_key', VAL_MISSED_ERR)

        if len(data.check_key) != PassFile.Constrains.CHECK_KEY_LEN:
            raise Bad('check_key', VAL_ERR, MORE.text("incorrect length"))

        if len(data.smth) < PassFile.Constrains.Raw.SMTH_MIN_LEN:
            raise Bad('smth', VAL_MISSED_ERR)

    @classmethod
    async def scheduled__check_archived_files(cls, context: 'SchedulerTask.Context') -> str:
        """ Delete old archived files (SchedulerTask).
        """
        expired = datetime.date.today() - datetime.timedelta(days=ARCHIVED_PASSFILE_LIFETIME_DAYS)

        async with context.db_utils.context_connection() as db:
            old_passfiles = await db.query_list(PassFile, cls._DELETE_OLD_ARCHIVED, {'expired_date': expired})

        for pf in old_passfiles:
            PassFileUtils.delete_file(pf)

        return ', '.join(str(p.id) for p in old_passfiles)

    # region SQL

    _SELECT_BY_USER_ID = MakeSql("""SELECT * FROM passfile WHERE user_id = @user_id""")

    _SELECT_BY_ID = MakeSql("""SELECT * FROM passfile WHERE id = @id""")

    _INSERT = MakeSql("""
        INSERT INTO passfile (name, user_id, color, check_key) 
        VALUES (@name, @user_id, @color, @check_key)
        RETURNING *
    """)

    _UPDATE_INFO = MakeSql("""
        UPDATE passfile SET (name, color, changed_on) = (@name, @color, now())
        WHERE id = @id
        RETURNING *
    """)

    _UPDATE_SMTH = MakeSql("""
        UPDATE passfile SET (version, check_key) = (@version, @check_key)
        WHERE id = @id
        RETURNING *
    """)

    _ARCHIVE = MakeSql("""UPDATE passfile SET archived_on = now() WHERE id = @id RETURNING *""")

    _UNARCHIVE = MakeSql("""UPDATE passfile SET archived_on = NULL WHERE id = @id RETURNING *""")

    _DELETE = MakeSql("""DELETE FROM passfile WHERE id = @id""")

    _DELETE_OLD_ARCHIVED = MakeSql("""DELETE FROM passfile WHERE archived_on < @expired_date RETURNING *""")

    # endregion
