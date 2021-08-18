from App.settings import PASS_FILES_FOLDER, PASS_FILES_ARCHIVE_FOLDER, KEY_PHRASE_BYTES
from cryptography.fernet import Fernet
import os
import aiofiles

__all__ = (
    'PassFileUtils',
)


class PassFileUtils:
    @classmethod
    def make_filepath_normal(cls, passfile_id: int, user_id: int) -> str:
        return os.path.join(PASS_FILES_FOLDER, str(user_id), str(passfile_id) + ".tmp")

    @classmethod
    def make_filepath_archived(cls, passfile_id: int) -> str:
        return os.path.join(PASS_FILES_ARCHIVE_FOLDER, str(passfile_id) + ".tmp")

    @classmethod
    def get_filepath(cls, passfile: 'PassFile') -> str:
        if passfile.is_archived:
            return cls.make_filepath_archived(passfile.id)
        return cls.make_filepath_normal(passfile.id, passfile.user_id)

    @classmethod
    def ensure_folders_created(cls):
        if not os.path.exists(PASS_FILES_FOLDER):
            os.mkdir(PASS_FILES_FOLDER)

        if not os.path.exists(PASS_FILES_ARCHIVE_FOLDER):
            os.mkdir(PASS_FILES_ARCHIVE_FOLDER)

    @classmethod
    async def write_file(cls, passfile: 'PassFile', content: str) -> bool:
        try:
            bytes_content = Fernet(KEY_PHRASE_BYTES).encrypt(content.encode('utf-8'))

            folder = os.path.join(PASS_FILES_FOLDER, str(passfile.user_id))
            file = os.path.join(folder, str(passfile.id) + ".tmp")

            if not os.path.exists(folder):
                os.mkdir(folder)

            async with aiofiles.open(file, 'wb') as f:
                await f.write(bytes_content)
        except Exception as e:
            pass  # TODO: log
            return False
        else:
            return True

    @classmethod
    def archive_file(cls, passfile: 'PassFile') -> bool:
        try:
            file = cls.make_filepath_normal(passfile.id, passfile.user_id)
            if os.path.exists(file):
                os.replace(file, cls.make_filepath_archived(passfile.id))
        except Exception as e:
            pass  # TODO: log critical
            return False
        else:
            return True

    @classmethod
    async def read_file(cls, passfile: 'PassFile') -> bytes:
        if passfile.is_archived:
            file = cls.make_filepath_archived(passfile.id)
        else:
            file = cls.make_filepath_normal(passfile.id, passfile.user_id)

        async with aiofiles.open(file, 'rb') as f:
            return Fernet(KEY_PHRASE_BYTES).decrypt(await f.read())


if True:
    from App.models.db import PassFile
