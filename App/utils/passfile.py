from App.settings import (
    PASSFILES_FOLDER,
    PASSFILES_ENCODING
)
from App.special import *
from App.database import PassFileVersion
from App.utils.crypto import CryptoUtils
from App.utils.logging import Logger

import aiofiles
import os
import re

__all__ = (
    'PassFileUtils',
)

logger = Logger(__file__)


class PassFileUtils:
    FILENAME_PATTERN = re.compile(r'^\d*v\d*_\d*.pf$')  # <passfile_id>v<version>.pf  TODO: use in auto-managing

    @classmethod
    def get_filepath(cls, pfv: 'PassFileVersion') -> str:
        """ Get passfile path in format '<PASSFILES_FOLDER>/<user_id>/<filename>'.

        :return: String path.
        """
        assert pfv.user_id is not None, "User Id Is Not Provided"

        return os.path.join(PASSFILES_FOLDER, str(pfv.user_id), f"{pfv.passfile_id}v{pfv.version}.pf")

    @classmethod
    async def write_file(cls, pfv: 'PassFileVersion', content: str):
        """ Write passfile content bytes to the file system
            by path corresponding to the specified version.

        :raise: Bad.
        """
        path = cls.get_filepath(pfv)
        bytes_content = CryptoUtils.encrypt_passfile_smth(content.encode(PASSFILES_ENCODING))

        try:
            directory = os.path.dirname(path)

            if not os.path.exists(directory):
                os.mkdir(directory)

            async with aiofiles.open(path, 'wb') as f:
                await f.write(bytes_content)
        except Exception as e:
            logger.critical(f"File writing error! (path: {path})", e)
            raise Bad(None, UNKNOWN_ERR, MORE.exception(e))

    @classmethod
    async def read_file(cls, pfv: 'PassFileVersion') -> bytes:
        """ Read passfile content bytes from the file system
            by path corresponding to the specified version.

        :raise: Bad.
        :return: Byte array.
        """
        path = cls.get_filepath(pfv)

        try:
            async with aiofiles.open(path, 'rb') as f:
                content = await f.read()
        except Exception as e:
            logger.critical(f"File reading error! (path: {path})", e)
            raise Bad(None, UNKNOWN_ERR)
        else:
            return CryptoUtils.decrypt_passfile_smth(content)

    @classmethod
    def delete_file(cls, pfv: 'PassFileVersion'):
        """ Delete passfile from the file system.

        :raise: Bad.
        """
        path = cls.get_filepath(pfv)

        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.critical(f"File deleting error! (path: {path})", e)
            raise Bad(None, UNKNOWN_ERR, MORE.exception(e))

    @classmethod
    def ensure_folders_created(cls):
        """ Create system directories if required.
        """
        if not os.path.exists(PASSFILES_FOLDER):
            os.makedirs(PASSFILES_FOLDER)
