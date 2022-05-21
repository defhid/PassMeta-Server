from App.services.base import DbServiceBase
from App.services import UserService
from App.special import *

from App.models.dto import PassfileNewDto, PassfileInfoPatchDto, PassfileSmthPatchDto
from App.models.entities import RequestInfo
from App.models.enums import HistoryKind

from App.database import MakeSql, User, PassFile
from App.utils.crypto import CryptoUtils
from App.utils.passfile import PassFileUtils

import re
import datetime

__all__ = (
    'PassFileService',
)


class PassFileService(DbServiceBase):
    __slots__ = ()

    async def get_user_passfiles(self, user: User, type_id: Optional[int]) -> List[PassFile]:
        return await self.db.query_list(PassFile, self._SELECT_BY_USER_ID, {
            'user_id': user.id,
            'type_id': type_id if type_id is not None else MakeSql('type_id')
        })

    async def get_file(self, passfile_id: int, version: Optional[int], request: RequestInfo) -> (PassFile, bytes):
        """ Raises: Bad [NOT_EXIST_ERR, ACCESS_ERR].
        """
        passfile = await self._get_passfile_or_raise(passfile_id)

        if passfile.user_id != request.user_id:
            await self.history_writer.write(HistoryKind.GET_PASSFILE_FAILURE,
                                            request.user_id, passfile.user_id,
                                            more=f"ACCESS,pf:{passfile.id}", request=request)
            raise Bad('passfile_id', ACCESS_ERR)

        await self.history_writer.write(HistoryKind.GET_PASSFILE_SUCCESS,
                                        request.user_id, passfile.user_id,
                                        more=f"pf:{passfile.id}", request=request)

        return passfile, await PassFileUtils.read_file(passfile, version)

    async def add_file(self, data: PassfileNewDto, request: RequestInfo) -> PassFile:
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
                'type_id': data.type_id,
                'created_on': data.created_on,
            })

            result = await PassFileUtils.write_file(passfile, data.smth)
            result.raise_if_failure()

            await self.history_writer.write(HistoryKind.CREATE_PASSFILE_SUCCESS,
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
                             data: PassfileInfoPatchDto, request: RequestInfo) -> PassFile:
        """ Raises: Bad.
        """
        self._validate_info(data)

        passfile = await self._get_passfile_or_raise(passfile_id)

        if passfile.user_id != request.user_id:
            await self.history_writer.write(HistoryKind.EDIT_PASSFILE_INFO_FAILURE,
                                            request.user_id, passfile.user_id,
                                            more=f"ACCESS,pf:{passfile.id}", request=request)
            raise Bad(None, ACCESS_ERR)

        passfile.name = data.name
        passfile.color = data.color

        async with self.db.transaction():
            passfile = await self.db.query_first(PassFile, self._UPDATE_INFO, passfile)

            await self.history_writer.write(HistoryKind.EDIT_PASSFILE_INFO_SUCCESS,
                                            request.user_id, passfile.user_id,
                                            more=f"pf:{passfile.id}", request=request)
        return passfile

    async def edit_file_smth(self, passfile_id: int,
                             data: PassfileSmthPatchDto, request: RequestInfo) -> PassFile:
        """ Raises: Bad.
        """
        self._validate_smth(data)

        passfile = await self._get_passfile_or_raise(passfile_id)

        if passfile.user_id != request.user_id:
            await self.history_writer.write(HistoryKind.EDIT_PASSFILE_SMTH_FAILURE,
                                            request.user_id, passfile.user_id,
                                            more=f"ACCESS,pf:{passfile.id}", request=request)
            raise Bad(None, ACCESS_ERR)

        passfile.version += 1

        result = await PassFileUtils.write_file(passfile, data.smth)
        result.raise_if_failure()

        transaction = self.db.transaction()
        try:
            await transaction.start()
            passfile = await self.db.query_first(PassFile, self._UPDATE_SMTH, passfile)

            await self.history_writer.write(HistoryKind.EDIT_PASSFILE_SMTH_SUCCESS,
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

    async def delete_file(self, passfile_id: int, check_password: str, request: RequestInfo):
        """ Raises: Bad.
        """
        passfile = await self._get_passfile_or_raise(passfile_id)

        user = await UserService(self.db).get_user_by_id(request.user_id)

        if not CryptoUtils.check_user_password(check_password, user.pwd):
            await self.history_writer.write(HistoryKind.DELETE_PASSFILE_FAILURE,
                                            request.user_id, passfile.user_id,
                                            more=f"ACCESS,pf:{passfile.id}", request=request)
            raise Bad("check_password", WRONG_VAL_ERR)

        async with self.db.transaction():
            await self.db.execute(self._DELETE, passfile)

            await self.history_writer.write(HistoryKind.DELETE_PASSFILE_SUCCESS,
                                            request.user_id, passfile.user_id,
                                            more=f"pf:{passfile.id}", request=request)

        PassFileUtils.delete_file(passfile)

    async def _get_passfile_or_raise(self, passfile_id: int) -> PassFile:
        passfile = await self.db.query_first(PassFile, self._SELECT_BY_ID, {'id': passfile_id})
        if passfile is None:
            raise Bad('passfile_id', NOT_EXIST_ERR)

        return passfile

    @classmethod
    def _validate_post_data(cls, data: PassfileNewDto):
        cls._validate_info(data)
        cls._validate_smth(data)

        if data.created_on.timestamp() > datetime.datetime.now().timestamp():
            raise Bad('created_on', TOO_MUCH_ERR, MORE.max_allowed(str(datetime.datetime.now())))

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
            if not re.fullmatch(re.compile(r'^[\dA-F]{6}$'), data.color):
                errors.append(Bad('color', VAL_ERR, MORE.allowed("HEX")))

        if errors:
            raise Bad(None, DATA_ERR, sub=errors)

    @staticmethod
    def _validate_smth(data):
        if len(data.smth) < PassFile.Constrains.Raw.SMTH_MIN_LEN:
            raise Bad('smth', VAL_MISSED_ERR)

    # region SQL

    _SELECT_BY_USER_ID = MakeSql("""SELECT * FROM passfiles WHERE user_id = @user_id""")

    _SELECT_BY_ID = MakeSql("""SELECT * FROM passfiles WHERE id = @id""")

    _INSERT = MakeSql("""
        INSERT INTO passfiles (name, user_id, color, type_id, created_on, info_changed_on, version_changed_on) 
        VALUES (@name, @user_id, @color, @type_id, @created_on, now(), now())
        RETURNING *
    """)

    _UPDATE_INFO = MakeSql("""
        UPDATE passfiles SET (name, color, info_changed_on) = (@name, @color, now())
        WHERE id = @id
        RETURNING *
    """)

    _UPDATE_SMTH = MakeSql("""
        UPDATE passfiles SET (version, version_changed_on) = (@version, now())
        WHERE id = @id
        RETURNING *
    """)

    _DELETE = MakeSql("""DELETE FROM passfiles WHERE id = @id""")

    # endregion
