from App.settings import PASSFILES_FOLDER
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
    FILENAME_PATTERN = re.compile(r'^\d*v\d*_\d*.pf$')  # <passfile_id>v<version>.pf

    @classmethod
    def get_filepath(cls, pfv: 'PassFileVersion') -> str:
        """ Get passfile path in format '<PASSFILES_FOLDER>/<user_id>/<filename>'.

        :return: String path.
        """
        assert pfv.user_id is not None, "User Id Is Not Provided"

        return os.path.join(PASSFILES_FOLDER, str(pfv.user_id), f"{pfv.passfile_id}v{pfv.version}.pf")

    @classmethod
    async def write_file(cls, pfv: 'PassFileVersion', content: bytes):
        """ Write passfile content bytes to the file system
            by path corresponding to the specified version.

        :raise: Bad.
        """
        path = cls.get_filepath(pfv)
        bytes_content = CryptoUtils.encrypt_passfile_smth(content)

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
        """
        path = cls.get_filepath(pfv)

        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception as e:
            logger.critical(f"File deleting error! (path: {path})", e)

    @classmethod
    def ensure_folders_created(cls):
        """ Create system directories if required.
        """
        if not os.path.exists(PASSFILES_FOLDER):
            os.makedirs(PASSFILES_FOLDER)

    # @classmethod
    # async def collect_garbage(cls, get_user_passfiles: Callable[[int, int], Coroutine[None, None, Set[int]]]) \
    #         -> List[str]:
    #     removed = []
    #
    #     def remove_file(path):
    #         os.remove(path)
    #         removed.append(path[len(PASSFILES_FOLDER) + 1:])
    #
    #     def remove_directory(path):
    #         shutil.rmtree(path)
    #         removed.append(path[len(PASSFILES_FOLDER) + 1:])
    #
    #     items = os.listdir(PASSFILES_FOLDER)
    #     sub_item = None
    #     for i in range(len(items)):
    #         item = items[i]
    #         try:
    #             item_path = os.path.join(PASSFILES_FOLDER, item)
    #
    #             if not os.path.exists(item_path):
    #                 continue
    #
    #             if not os.path.isdir(item_path):
    #                 remove_file(item_path)
    #                 continue
    #
    #             if not item.isdigit():
    #                 remove_directory(item_path)
    #                 continue
    #
    #             user_id = int(item)
    #             passfiles_db = await get_user_passfiles(user_id, i)
    #
    #             if not passfiles_db:
    #                 remove_directory(item_path)
    #                 continue
    #
    #             for sub_item in os.listdir(item_path):
    #                 sub_item_path = os.path.join(item_path, sub_item)
    #
    #                 if not os.path.isfile(sub_item_path):
    #                     remove_directory(sub_item_path)
    #                     continue
    #
    #                 if cls.FILENAME_PATTERN.fullmatch(sub_item):
    #                     if int(sub_item.split("v")[0]) not in passfiles_db:
    #                         continue
    #
    #                 remove_file(item_path)
    #         except Exception as e:
    #             logger.error(f"Garbage removing error! (path items: {item}, {sub_item})", e)
    #
    #     return removed
