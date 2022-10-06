from App.services.base import DbServiceBase
from App.services import UserService
from App.special import *

from App.models.dto import PassfileNewDto, PassfileInfoPatchDto, PassfileSmthPatchDto
from App.models.entities import RequestInfo
from App.models.enums import HistoryKind

from App.database import MakeSql, User, PassFile, PassFileVersion
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
        """ Raises: Bad.
        """
        passfile = await self._get_passfile_or_raise(passfile_id)

        if passfile.user_id != request.user_id:
            await self.history_writer.write(HistoryKind.GET_PASSFILE_FAILURE,
                                            request.user_id, passfile.user_id, passfile.id, "ACCESS")
            raise Bad('passfile_id', ACCESS_ERR)

        try:
            passfile_version = await self._get_passfile_version_or_raise(
                passfile.id,
                version if version is not None else passfile.version
            )

            smth = await PassFileUtils.read_file(passfile_version)
        except Exception:
            await self.history_writer.write(HistoryKind.GET_PASSFILE_FAILURE,
                                            request.user_id, passfile.user_id, passfile.id, "EXCEPTION")
            raise
        else:
            await self.history_writer.write(HistoryKind.GET_PASSFILE_SUCCESS,
                                            request.user_id, passfile.user_id, passfile.id)

        return passfile, smth

    async def add_file(self, data: PassfileNewDto, request: RequestInfo) -> PassFile:
        """ Raises: Bad.
        """
        self._validate_post_data(data)

        passfile_version = None
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
            passfile_version = await self.db.query_first(PassFileVersion, self._INSERT_VERSION, {
                'passfile_id': passfile.id,
            })
            passfile_version.user_id = passfile.user_id

            await PassFileUtils.write_file(passfile_version, data.smth)

            await self.history_writer.write(HistoryKind.CREATE_PASSFILE_SUCCESS,
                                            request.user_id, request.user_id, passfile.id)
        except Exception:
            await transaction.rollback()
            if passfile_version:
                try:
                    PassFileUtils.delete_file(passfile_version)
                finally:
                    pass
            await self.history_writer.write(HistoryKind.CREATE_PASSFILE_FAILURE,
                                            request.user_id, request.user_id, None, "EXCEPTION")
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
                                            request.user_id, passfile.user_id, passfile.id, "ACCESS")
            raise Bad(None, ACCESS_ERR)

        try:
            passfile.name = data.name
            passfile.color = data.color

            async with self.db.transaction():
                passfile = await self.db.query_first(PassFile, self._UPDATE_INFO, passfile)

                await self.history_writer.write(HistoryKind.EDIT_PASSFILE_INFO_SUCCESS,
                                                request.user_id, passfile.user_id, passfile.id)
        except Exception:
            await self.history_writer.write(HistoryKind.EDIT_PASSFILE_INFO_FAILURE,
                                            request.user_id, passfile.user_id, passfile.id, "EXCEPTION")
            raise

        return passfile

    async def edit_file_smth(self, passfile_id: int,
                             data: PassfileSmthPatchDto, request: RequestInfo) -> PassFile:
        """ Raises: Bad.
        """
        self._validate_smth(data)

        passfile = await self._get_passfile_or_raise(passfile_id)

        if passfile.user_id != request.user_id:
            await self.history_writer.write(HistoryKind.EDIT_PASSFILE_SMTH_FAILURE,
                                            request.user_id, passfile.user_id, passfile.id, "ACCESS")
            raise Bad(None, ACCESS_ERR)

        passfile_version = None

        transaction = self.db.transaction()
        try:
            await transaction.start()

            passfile.version += 1
            passfile = await self.db.query_first(PassFile, self._UPDATE_SMTH, passfile)

            passfile_version = await self.db.query_first(PassFileVersion, self._INSERT_VERSION, {
                'passfile_id': passfile.id,
            })
            passfile_version.user_id = passfile.user_id

            # TODO: manage previous versions

            await PassFileUtils.write_file(passfile_version, data.smth)

            await self.history_writer.write(HistoryKind.EDIT_PASSFILE_SMTH_SUCCESS,
                                            request.user_id, passfile.user_id, passfile.id)
        except Exception:
            await transaction.rollback()
            if passfile_version:
                try:
                    PassFileUtils.delete_file(passfile_version)
                finally:
                    pass
            await self.history_writer.write(HistoryKind.CREATE_PASSFILE_FAILURE,
                                            request.user_id, request.user_id, None, "EXCEPTION")
            raise
        else:
            await transaction.commit()

        return passfile

    @classmethod
    def optimize_file_versions(cls, passfile: 'PassFile') -> Result:
        """ Delete excess passfile versions from file system.

        :return: Success.
        """
        pass
        # TODO
        # paths = cls.get_filepath_list(passfile)
        # try:
        #     for i in range(min(len(paths) - PASSFILE_KEEP_VERSIONS, len(paths) - 1)):
        #         os.remove(paths[i].full_path)
        # except Exception as e:
        #     logger.critical("File versions optimizing error!", e)
        #     return Bad(None, UNKNOWN_ERR, MORE.exception(e))
        # else:
        #     return Ok()

    async def delete_file(self, passfile_id: int, check_password: str, request: RequestInfo):
        """ Raises: Bad.
        """
        passfile = await self._get_passfile_or_raise(passfile_id)

        user = await UserService(self.db).get_user_by_id(request.user_id)

        if not CryptoUtils.check_user_password(check_password, user.pwd):
            await self.history_writer.write(HistoryKind.DELETE_PASSFILE_FAILURE,
                                            request.user_id, passfile.user_id, passfile.id, "ACCESS")
            raise Bad("check_password", WRONG_VAL_ERR)

        try:
            passfile_versions = await self.db.query_list(PassFileVersion, self._SELECT_VERSION_LIST, {
                'passfile_id': passfile.id,
            })

            for passfile_version in passfile_versions:
                PassFileUtils.delete_file(passfile_version)
                await self.db.execute(self._DELETE_VERSION, passfile_version)

            async with self.db.transaction():
                await self.db.execute(self._DELETE, passfile)

                await self.history_writer.write(HistoryKind.DELETE_PASSFILE_SUCCESS,
                                                request.user_id, passfile.user_id, passfile.id)
        except Exception:
            await self.history_writer.write(HistoryKind.DELETE_PASSFILE_FAILURE,
                                            request.user_id, passfile.user_id, passfile.id, "EXCEPTION")
            raise

    async def _get_passfile_or_raise(self, passfile_id: int) -> PassFile:
        passfile = await self.db.query_first(PassFile, self._SELECT_BY_ID, {'id': passfile_id})
        if passfile is None:
            raise Bad('passfile_id', NOT_EXIST_ERR)

        return passfile

    async def _get_passfile_version_or_raise(self, passfile_id: int, version: int) -> PassFileVersion:
        passfile_version = await self.db.query_first(PassFileVersion, self._SELECT_VERSION, {
            'passfile_id': passfile_id,
            'version': version,
        })

        if passfile_version is None:
            raise Bad('version', NOT_EXIST_ERR)

        return passfile_version

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

    _SELECT_VERSION = MakeSql("""
        SELECT pfv.*, pf.user_id
        FROM passfile_versions pfv
            JOIN passfiles pf ON pf.id = pfv.passfile_id
        WHERE passfile_id = @passfile_id AND version = @version
    """)

    _SELECT_VERSION_LIST = MakeSql("""
        SELECT pfv.*, pf.user_id
        FROM passfile_versions pfv
            JOIN passfiles pf ON pf.id = pfv.passfile_id
        WHERE passfile_id = @passfile_id
        ORDER BY pfv.version
    """)

    _INSERT = MakeSql("""
        INSERT INTO passfiles (name, user_id, color, type_id, created_on, info_changed_on, version_changed_on) 
        VALUES (@name, @user_id, @color, @type_id, @created_on, now(), now())
        RETURNING *
    """)

    _INSERT_VERSION = MakeSql("""
        INSERT INTO passfile_versions (passfile_id, version, version_date) 
        SELECT id, version, version_changed_on FROM passfiles WHERE id = @passfile_id
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

    _DELETE_VERSION = MakeSql("""
        DELETE FROM passfile_versions
        WHERE passfile_id = @passfile_id AND version = @version
    """)

    # endregion
