from App.models.okbad import *
from App.services.base import DbServiceBase
from App.services import UserService
from App.settings import PASSFILE_KEEP_DAY_VERSIONS, PASSFILE_KEEP_VERSIONS

from App.models.dto.requests import PassfilePostDto, PassfilePatchDto
from App.models.enums import HistoryKind

from App.database import MakeSql, User, PassFile, PassFileVersion
from App.utils.crypto import CryptoUtils
from App.utils.passfile import PassFileUtils, ExcessVersionsFinder

import re
import datetime

__all__ = (
    'PassFileService',
)


class PassFileService(DbServiceBase):
    __slots__ = ()

    EXCESS_VERSIONS_FINDER = ExcessVersionsFinder(PASSFILE_KEEP_VERSIONS, PASSFILE_KEEP_DAY_VERSIONS)

    async def get_user_passfiles(self, user: User, type_id: int | None) -> list[PassFile]:
        """ Raises: Bad.
        """
        async with self.history_writer.operation(
                HistoryKind.GET_PASSFILE_LIST_SUCCESS,
                HistoryKind.GET_PASSFILE_LIST_FAILURE,
                affected_user_id=user.id,
        ):
            return await self.db.query_list(PassFile, self._SELECT_LIST_BY_USER_ID, {
                'user_id': user.id,
                'type_id': type_id if type_id is not None else MakeSql('type_id')
            })

    async def get_passfile(self, passfile_id: int) -> PassFile:
        """ Raises: Bad.
        """
        async with self.history_writer.operation(
                HistoryKind.GET_PASSFILE_INFO_SUCCESS,
                HistoryKind.GET_PASSFILE_INFO_FAILURE,
                affected_passfile_id=passfile_id,
        ) as history_operation:
            passfile = await self._get_passfile_or_raise(passfile_id)

            history_operation.with_affected_user(passfile.user_id)
    
            if passfile.user_id != self.request.user_id:
                raise Bad('passfile_id', ACCESS_ERR)

            return passfile

    async def get_passfile_smth(self, passfile_id: int, version: int | None) -> bytes:
        """ Raises: Bad.
        """
        async with self.history_writer.operation(
                HistoryKind.GET_PASSFILE_SMTH_SUCCESS,
                HistoryKind.GET_PASSFILE_SMTH_FAILURE,
                affected_passfile_id=passfile_id,
        ) as history_operation:
            passfile_version = await self.db.query_first(PassFileVersion, self._SELECT_VERSION, {
                'passfile_id': passfile_id,
                'version': version,
            })

            if passfile_version is None:
                if version is None:
                    return bytes()
                raise Bad('version', NOT_EXIST_ERR)

            history_operation.with_affected_user(passfile_version.user_id)
    
            if passfile_version.user_id != self.request.user_id:
                raise Bad('passfile_id', ACCESS_ERR)

            return await PassFileUtils.read_file(passfile_version)

    async def get_passfile_versions(self, passfile_id: int) -> list[PassFileVersion]:
        """ Raises: Bad.
        """
        async with self.history_writer.operation(
                HistoryKind.GET_PASSFILE_INFO_SUCCESS,
                HistoryKind.GET_PASSFILE_INFO_FAILURE,
                affected_passfile_id=passfile_id,
        ) as history_operation:
            passfile = await self._get_passfile_or_raise(passfile_id)

            history_operation.with_affected_user(passfile.user_id)
    
            if passfile.user_id != self.request.user_id:
                raise Bad('passfile_id', ACCESS_ERR)
    
            versions = await self.db.query_list(PassFileVersion, self._SELECT_VERSION_LIST, {
                'passfile_id': passfile.id
            })

        return versions

    async def add_passfile(self, data: PassfilePostDto) -> PassFile:
        """ Raises: Bad.
        """
        async with self.history_writer.operation(
                HistoryKind.CREATE_PASSFILE_SUCCESS,
                HistoryKind.CREATE_PASSFILE_FAILURE,
                affected_user_id=self.request.user_id,
        ) as history_operation:
            self._validate_post_data(data)

            await history_operation.start_db_transaction()

            passfile = await self.db.query_first(PassFile, self._INSERT, {
                'user_id': self.request.user_id,
                'name': data.name,
                'color': data.color,
                'type_id': data.type_id,
                'created_on': data.created_on,
                'info_changed_on': datetime.datetime.utcnow(),
                'version_changed_on': datetime.datetime.utcnow(),
            })

            history_operation.with_affected_passfile(passfile.id)

        return passfile

    async def edit_passfile_info(self, passfile_id: int, data: PassfilePatchDto) -> PassFile:
        """ Raises: Bad.
        """
        async with self.history_writer.operation(
                HistoryKind.EDIT_PASSFILE_INFO_SUCCESS,
                HistoryKind.EDIT_PASSFILE_INFO_FAILURE,
                affected_passfile_id=passfile_id,
        ) as history_operation:
            passfile = await self._get_passfile_or_raise(passfile_id)
            
            history_operation.with_affected_user(passfile.user_id)
            
            if passfile.user_id != self.request.user_id:
                raise Bad(None, ACCESS_ERR)

            self._validate_info(data)

            await history_operation.start_db_transaction()

            passfile.name = data.name
            passfile.color = data.color
            passfile.info_changed_on = datetime.datetime.utcnow()
            passfile = await self.db.query_first(PassFile, self._UPDATE_INFO, passfile)

        return passfile

    async def edit_passfile_smth(self, passfile_id: int, data: bytes) -> PassFile:
        """ Raises: Bad.
        """
        passfile_version = None
        try:
            async with self.history_writer.operation(
                    HistoryKind.EDIT_PASSFILE_SMTH_SUCCESS,
                    HistoryKind.EDIT_PASSFILE_SMTH_FAILURE,
                    affected_passfile_id=passfile_id,
            ) as history_operation:
                passfile = await self._get_passfile_or_raise(passfile_id)

                history_operation.with_affected_user(passfile.user_id)

                if passfile.user_id != self.request.user_id:
                    raise Bad(None, ACCESS_ERR)

                await history_operation.start_db_transaction()

                passfile.version_changed_on = datetime.datetime.utcnow()
                passfile = await self.db.query_first(PassFile, self._UPDATE_SMTH, passfile)

                passfile_version = await self._save_new_version(passfile, data)
        except Exception:
            if passfile_version is not None:
                PassFileUtils.delete_file(passfile_version)
            raise
        else:
            return passfile

    async def delete_passfile(self, passfile_id: int, check_password: str):
        """ Raises: Bad.
        """
        async with self.history_writer.operation(
                HistoryKind.DELETE_PASSFILE_SUCCESS,
                HistoryKind.DELETE_PASSFILE_FAILURE,
                affected_passfile_id=passfile_id,
        ) as history_operation:
            passfile = await self._get_passfile_or_raise(passfile_id)

            history_operation.with_affected_user(passfile.user_id)

            if passfile.user_id != self.request.user_id:
                raise Bad('passfile_id', ACCESS_ERR)

            user = await UserService(self.db, self.request).get_user_by_id(self.request.user_id)

            if not CryptoUtils.check_user_password(check_password, user.pwd):
                raise Bad("check_password", ACCESS_ERR)

            passfile_versions = await self.db.query_list(PassFileVersion, self._SELECT_VERSION_LIST, {
                'passfile_id': passfile.id,
            })

            for passfile_version in passfile_versions:
                PassFileUtils.delete_file(passfile_version)
                await self.db.execute(self._DELETE_VERSION, passfile_version)

            await history_operation.start_db_transaction()
            await self.db.execute(self._DELETE, passfile)

    async def _get_passfile_or_raise(self, passfile_id: int) -> PassFile:
        passfile = await self.db.query_first(PassFile, self._SELECT_BY_ID, {'id': passfile_id})
        if passfile is None:
            raise Bad('passfile_id', NOT_EXIST_ERR)

        return passfile

    async def _save_new_version(self, passfile: PassFile, smth: bytes) -> PassFileVersion:
        versions = await self.db.query_list(PassFileVersion, self._SELECT_VERSION_LIST, {'passfile_id': passfile.id})

        to_delete = self.EXCESS_VERSIONS_FINDER.find(versions)
        override = None

        if to_delete:
            override = to_delete.pop()

            PassFileUtils.delete_file(override)

            for version in to_delete:
                PassFileUtils.delete_file(version)

                await self.db.query_first(PassFileVersion, self._DELETE_VERSION, version)

        if override:
            new_version = await self.db.query_first(PassFileVersion, self._UPDATE_VERSION, {
                'passfile_id': passfile.id,
                'old_version': override.version,
            })
        else:
            new_version = await self.db.query_first(PassFileVersion, self._INSERT_VERSION, {
                'passfile_id': passfile.id,
            })

        new_version.user_id = passfile.user_id

        await PassFileUtils.write_file(new_version, smth)
        return new_version

    @classmethod
    def _validate_post_data(cls, data: PassfilePostDto):
        cls._validate_info(data)

        if data.created_on.timestamp() > datetime.datetime.now().timestamp():
            raise Bad('created_on', TOO_MUCH_ERR, MORE.max_allowed(f"UTC {datetime.datetime.utcnow()}"))

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

    # region SQL

    _SELECT_BY_ID = MakeSql("""SELECT * FROM passfiles WHERE id = #id""")

    _SELECT_LIST_BY_USER_ID = MakeSql("""SELECT * FROM passfiles WHERE user_id = #user_id AND type_id = #type_id""")

    _SELECT_ID_LIST_BY_USER_ID = MakeSql("""SELECT id FROM passfiles WHERE user_id = #user_id""")

    _INSERT = MakeSql("""
        INSERT INTO passfiles (name, user_id, color, type_id, created_on, info_changed_on, version_changed_on) 
        VALUES (#name, #user_id, #color, #type_id, #created_on, #info_changed_on, #version_changed_on)
        RETURNING *
    """)

    _UPDATE_INFO = MakeSql("""
        UPDATE passfiles SET (name, color, info_changed_on) = (#name, #color, #info_changed_on)
        WHERE id = #id
        RETURNING *
    """)

    _UPDATE_SMTH = MakeSql("""
        UPDATE passfiles SET (version, version_changed_on) = (version + 1, #version_changed_on)
        WHERE id = #id
        RETURNING *
    """)

    _DELETE = MakeSql("""DELETE FROM passfiles WHERE id = #id""")

    _SELECT_VERSION = MakeSql("""
        SELECT pfv.*, pf.user_id
        FROM passfile_versions pfv
            JOIN passfiles pf ON pf.id = pfv.passfile_id
        WHERE pfv.passfile_id = #passfile_id
          AND pfv.version = coalesce(#version, pfv.version)
        ORDER BY pfv.version DESC
        LIMIT 1
    """)

    _SELECT_VERSION_LIST = MakeSql("""
        SELECT pfv.*, pf.user_id
        FROM passfile_versions pfv
            JOIN passfiles pf ON pf.id = pfv.passfile_id
        WHERE passfile_id = #passfile_id
        ORDER BY pfv.version
    """)

    _INSERT_VERSION = MakeSql("""
        INSERT INTO passfile_versions (passfile_id, version, version_date)
        SELECT pf.id, pf.version, version_changed_on
        FROM passfiles pf
        WHERE pf.id = #passfile_id
        RETURNING *
    """)

    _UPDATE_VERSION = MakeSql("""
        UPDATE passfile_versions pfv
        SET version = pf.version,
            version_date = pf.version_changed_on
        FROM passfiles pf
        WHERE pf.id = #passfile_id
          AND pfv.passfile_id = pf.id
          AND pfv.version = #old_version
        RETURNING *
    """)

    _DELETE_VERSION = MakeSql("""
        DELETE FROM passfile_versions
        WHERE passfile_id = #passfile_id AND version = #version
    """)

    # endregion
