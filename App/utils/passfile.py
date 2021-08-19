from App.settings import PASSFILES_FOLDER, PASSFILES_ARCHIVE_FOLDER, KEY_PHRASE_BYTES, ARCHIVED_PASSFILE_LIFETIME_DAYS
from App.models.db import PassFile
from App.utils.db import DbUtils

from sqlalchemy import select
from cryptography.fernet import Fernet
from typing import Optional
from datetime import datetime, timedelta

import aiofiles
import logging
import os

__all__ = (
    'PassFileUtils',
)

logger = logging.getLogger(__name__)


class PassFileUtils:
    @classmethod
    def ensure_folders_created(cls):
        """ Ensure system directories exist (create if not).
        """
        if not os.path.exists(PASSFILES_FOLDER):
            os.mkdir(PASSFILES_FOLDER)

        if not os.path.exists(PASSFILES_ARCHIVE_FOLDER):
            os.mkdir(PASSFILES_ARCHIVE_FOLDER)

    @classmethod
    def _make_filepath_normal(cls, user_id: int, passfile_id: int) -> str:
        """ Generates passfile path in format '<PASS_FILES_FOLDER>/<user_id>/<passfile_id>.tmp'.
            :returns string path.
        """
        return os.path.join(PASSFILES_FOLDER, str(user_id), str(passfile_id) + ".tmp")

    @classmethod
    def _make_filepath_archived(cls, passfile_id: int) -> str:
        """ Generates passfile archive path in format '<PASS_FILES_ARCHIVE_FOLDER>/<passfile_id>.tmp'.
            :returns string path.
        """
        return os.path.join(PASSFILES_ARCHIVE_FOLDER, str(passfile_id) + ".tmp")

    @classmethod
    def get_filepath(cls, passfile: 'PassFile') -> str:
        """ Get passfile path depending on its is_archived flag.
            :returns string path.
        """
        if passfile.is_archived:
            return cls._make_filepath_archived(passfile.id)
        return cls._make_filepath_normal(passfile.user_id, passfile.id)

    @classmethod
    async def write_file(cls, passfile: 'PassFile', content: str) -> bool:
        """ Write passfile content to its normal path.
            :returns content written successfully?
        """
        try:
            bytes_content = Fernet(KEY_PHRASE_BYTES).encrypt(content.encode('utf-8'))

            path = cls._make_filepath_normal(passfile.user_id, passfile.id)
            if not os.path.exists(os.path.dirname(path)):
                os.mkdir(path)

            async with aiofiles.open(path, 'wb') as f:
                await f.write(bytes_content)
        except Exception as e:
            logger.critical("File writing error!", e)
            return False
        else:
            return True

    @classmethod
    def archive_file(cls, passfile: 'PassFile') -> bool:
        """ Move file from normal path to archived.
            :returns file moved successfully?
        """
        try:
            path_normal = cls._make_filepath_normal(passfile.user_id, passfile.id)
            path_archived = cls._make_filepath_archived(passfile.id)

            if os.path.exists(path_normal):
                os.replace(path_normal, path_archived)

            assert not os.path.exists(path_archived), "File Does Not Exist"
        except Exception as e:
            logger.critical("File archiving error!", e)
            return False
        else:
            return True

    @classmethod
    async def read_file(cls, passfile: 'PassFile') -> Optional[bytes]:
        """ Read file bytes from current passfile path.
            :returns byte array — file exists, None — file not found.
        """
        if passfile.is_archived:
            file = cls._make_filepath_archived(passfile.id)
        else:
            file = cls._make_filepath_normal(passfile.user_id, passfile.id)

        try:
            async with aiofiles.open(file, 'rb') as f:
                return Fernet(KEY_PHRASE_BYTES).decrypt(await f.read())
        except Exception as e:
            logger.critical("File reading error!", e)
            return None

    @classmethod
    async def check_archive_files(cls):
        expired = datetime.now() - timedelta(days=ARCHIVED_PASSFILE_LIFETIME_DAYS)
        async with DbUtils.make_session() as db:
            for passfile in await db.query(PassFile, select(PassFile).where(PassFile.created_on < expired)):
                await db.delete(passfile)
                path = cls.get_filepath(passfile)
                if os.path.exists(path):
                    os.remove(path)
                await db.commit()

