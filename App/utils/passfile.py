from App.settings import (
    PASSFILES_FOLDER,
    PASSFILES_ARCHIVE_FOLDER,
    KEY_PHRASE_BYTES,
    PASSFILE_KEEP_VERSIONS
)
from App.special import *
from App.models.db import PassFile
from App.utils.logging import Logger

from cryptography.fernet import Fernet
import aiofiles
import os

__all__ = (
    'PassFileUtils',
)

logger = Logger(__name__)


class PassFileUtils:
    @classmethod
    def _make_filepath_normal(cls, user_id: int, passfile_id: int, passfile_version: int) -> str:
        """ Generates passfile path in format '<PASS_FILES_FOLDER>/<user_id>/<passfile_id>v<version>.tmp'.

        :return: String path.
        """
        return os.path.join(PASSFILES_FOLDER, str(user_id), f"{passfile_id}v{passfile_version}.tmp")

    @classmethod
    def _make_filepath_archived(cls, passfile_id: int) -> str:
        """ Generates passfile archive path in format '<PASS_FILES_ARCHIVE_FOLDER>/<passfile_id>.tmp'.

        :return: String path.
        """
        return os.path.join(PASSFILES_ARCHIVE_FOLDER, f"{passfile_id}.tmp")

    @classmethod
    def get_filepath(cls, passfile: 'PassFile') -> str:
        """ Get passfile path depending on its is_archived flag.

        :return: String path.
        """
        if passfile.is_archived:
            return cls._make_filepath_archived(passfile.id)
        return cls._make_filepath_normal(passfile.user_id, passfile.id, passfile.version)

    @classmethod
    async def write_file(cls, passfile: 'PassFile', content: str) -> Result:
        """ Write passfile content to its normal path.

        :return: Success.
        """
        try:
            bytes_content = Fernet(KEY_PHRASE_BYTES).encrypt(content.encode('utf-8'))
        except Exception as e:
            logger.critical("File encryption error!", e)
            return Bad(None, UNKNOWN_ERR, MORE.text("Server-Side Encryption Failed"))

        path = cls._make_filepath_normal(passfile.user_id, passfile.id, passfile.version)

        try:
            directory = os.path.dirname(path)

            if not os.path.exists(directory):
                os.mkdir(directory)

            async with aiofiles.open(path, 'wb') as f:
                await f.write(bytes_content)

            if not os.path.exists(path):
                return Bad(None, SERVER_ERR, MORE.text("Result File Does Not Exist"))
        except Exception as e:
            logger.critical("File writing error!", e)
            return Bad(None, UNKNOWN_ERR, MORE.exception(e))
        else:
            return Ok()

    @classmethod
    def archive_file(cls, passfile: 'PassFile') -> Result:
        """ Move passfile from normal path to archived.

        :return: Success.
        """
        path_normal = cls._make_filepath_normal(passfile.user_id, passfile.id, passfile.version)
        path_archived = cls._make_filepath_archived(passfile.id)

        try:
            if not os.path.exists(path_normal):
                return Bad(None, SERVER_ERR, MORE.text("Origin File Does Not Exist"))

            os.replace(path_normal, path_archived)

            if not os.path.exists(path_archived):
                return Bad(None, SERVER_ERR, MORE.text("Result File Does Not Exist"))
        except Exception as e:
            logger.critical("File archiving error!", e)
            return Bad(None, UNKNOWN_ERR, MORE.exception(e))
        else:
            return Ok()

    @classmethod
    def unarchive_file(cls, passfile: 'PassFile') -> Result:
        """ Move passfile from archived path to normal.

        :return: Success.
        """
        path_normal = cls._make_filepath_normal(passfile.user_id, passfile.id, passfile.version)
        path_archived = cls._make_filepath_archived(passfile.id)

        try:
            if not os.path.exists(path_archived):
                return Bad(None, SERVER_ERR, MORE.text("Origin File Does Not Exist"))

            os.replace(path_archived, path_normal)

            if not os.path.exists(path_normal):
                return Bad(None, SERVER_ERR, MORE.text("Result File Does Not Exist"))
        except Exception as e:
            logger.critical("File unarchiving error!", e)
            return Bad(None, UNKNOWN_ERR, MORE.exception(e))
        else:
            return Ok()

    @classmethod
    def optimize_file_versions(cls, passfile: 'PassFile') -> Result:
        """ Delete excess passfile versions from file system.

        :return: Success.
        """
        curr_path = cls._make_filepath_normal(passfile.user_id, passfile.id, passfile.version)

        try:
            directory = os.path.dirname(curr_path)

            if not os.path.exists(directory):
                return Bad(None, SERVER_ERR, MORE.text("User File Directory Does Not Exist"))

            passfile_id = str(passfile.id)

            items = map(lambda it: (it.split('v')[0], it.split('v')[1].split('.')[0], os.path.join(directory, it)),
                        os.listdir(directory))

            files = list(filter(lambda it: os.path.isfile(it[2]) and it[0] == passfile_id, items))
            files.sort(key=lambda it: int(it[1]))

            for i in range(min(len(files) - PASSFILE_KEEP_VERSIONS, len(files) - 1)):
                os.remove(files[i][2])

        except Exception as e:
            logger.critical("File versions optimizing error!", e)
            return Bad(None, UNKNOWN_ERR, MORE.exception(e))
        else:
            return Ok()

    @classmethod
    def delete_file(cls, passfile: 'PassFile') -> Result:
        """ Delete passfile from file system.

        :return: Success.
        """
        path = cls.get_filepath(passfile)

        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.critical(f"File '{path}' deleting error!", e)
            return Bad(None, UNKNOWN_ERR, MORE.exception(e))
        else:
            return Ok()

    @classmethod
    async def read_file(cls, passfile: 'PassFile') -> Optional[bytes]:
        """ Read passfile bytes from its current path.

        :return: Byte array — file exists,
                 None — file not found.
        """
        file = cls.get_filepath(passfile)

        try:
            async with aiofiles.open(file, 'rb') as f:
                return Fernet(KEY_PHRASE_BYTES).decrypt(await f.read())
        except Exception as e:
            logger.critical("File reading error!", e)
            return None

    @classmethod
    def ensure_folders_created(cls):
        """ Make system directories if not exist.
        """
        if not os.path.exists(PASSFILES_FOLDER):
            os.makedirs(PASSFILES_FOLDER)

        if not os.path.exists(PASSFILES_ARCHIVE_FOLDER):
            os.makedirs(PASSFILES_ARCHIVE_FOLDER)
