from App.settings import (
    PASSFILES_FOLDER,
    PASSFILES_ENCODING,
    PASSFILE_KEEP_VERSIONS
)
from App.special import *
from App.models.orm import PassFile
from App.models.entities import PassFilePath
from App.utils.crypto import CryptoUtils
from App.utils.logging import Logger

import aiofiles
import os

__all__ = (
    'PassFileUtils',
)

logger = Logger(__file__)


class PassFileUtils:
    @classmethod
    def get_filepath(cls, passfile: 'PassFile') -> str:
        """ Get passfile path in format '<PASS_FILES_FOLDER>/<user_id>/<passfile_id>v<version>.tmp'.

        :return: String path.
        """
        return os.path.join(PASSFILES_FOLDER, str(passfile.user_id), f"{passfile.id}v{passfile.version}.tmp")

    @classmethod
    def collect_filepath_list(cls, passfile: 'PassFile') -> List[PassFilePath]:
        """ Find all passfile paths (all versions) and sort them by version ascending.

        :return: List of string paths.
        """
        try:
            directory = os.path.dirname(cls.get_filepath(passfile))

            assert os.path.exists(directory), "User File Directory Does Not Exist"

            items = map(lambda it: PassFilePath(it, os.path.join(directory, it)), os.listdir(directory))

            files = list(filter(lambda it: os.path.isfile(it.full_path) and it.id == passfile.id, items))
            files.sort(key=lambda it: it.version)

            return files
        except Exception as e:
            logger.critical(f"Passfile paths finding error! (pf: {passfile.id})", e)
            return []

    @classmethod
    async def write_file(cls, passfile: 'PassFile', content: str) -> Result:
        """ Write passfile content to its normal path.

        :return: Success.
        """

        bytes_content = CryptoUtils.encrypt_passfile_smth(content.encode(PASSFILES_ENCODING))
        path = cls.get_filepath(passfile)

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
    async def read_file(cls, passfile: 'PassFile', version: int = None) -> Optional[bytes]:
        """ Read passfile bytes from its current path.

        :raise: Bad.
        :return: Byte array - if passfile has content,
                 None - if content does not exists.
        """
        if version is None:
            path = cls.get_filepath(passfile)
        else:
            paths = cls.collect_filepath_list(passfile)
            try:
                path = next(filter(lambda p: p.version == version, paths)).full_path
            except StopIteration:
                raise Bad('version', NOT_EXIST_ERR)

        try:
            if not os.path.exists(path):
                return None

            async with aiofiles.open(path, 'rb') as f:
                content = await f.read()
        except Exception as e:
            logger.critical(f"File reading error! (pf: {passfile.id})", e)
            raise Bad(None, UNKNOWN_ERR)
        else:
            return CryptoUtils.decrypt_passfile_smth(content)

    @classmethod
    def optimize_file_versions(cls, passfile: 'PassFile') -> Result:
        """ Delete excess passfile versions from file system.

        :return: Success.
        """
        paths = cls.collect_filepath_list(passfile)
        try:
            for i in range(min(len(paths) - PASSFILE_KEEP_VERSIONS, len(paths) - 1)):
                os.remove(paths[i].full_path)
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
        paths = cls.collect_filepath_list(passfile)
        path = None
        try:
            for path in paths:
                if os.path.exists(path.full_path):
                    os.remove(path.full_path)
        except Exception as e:
            logger.critical(f"File '{path}' deleting error!", e)
            return Bad(None, UNKNOWN_ERR, MORE.exception(e))
        else:
            return Ok()

    @classmethod
    def ensure_folders_created(cls):
        """ Make system directories if not exist.
        """
        if not os.path.exists(PASSFILES_FOLDER):
            os.makedirs(PASSFILES_FOLDER)
