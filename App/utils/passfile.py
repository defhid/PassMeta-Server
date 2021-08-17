from App.settings import PASS_FILES_FOLDER, PASS_FILES_ARCHIVE_FOLDER, KEY_PHRASE_BYTES
from cryptography.fernet import Fernet
import os

__all__ = (
    'PassFileUtils',
)


class PassFileUtils:
    @staticmethod
    def make_filepath_normal(passfile_id: int, user_id: int) -> str:
        return os.path.join(PASS_FILES_FOLDER, str(user_id), str(passfile_id) + ".tmp")

    @staticmethod
    def make_filepath_archived(passfile_id: int) -> str:
        return os.path.join(PASS_FILES_ARCHIVE_FOLDER, str(passfile_id) + ".tmp")

    @staticmethod
    def ensure_folders_created():
        if not os.path.exists(PASS_FILES_FOLDER):
            os.mkdir(PASS_FILES_FOLDER)

        if not os.path.exists(PASS_FILES_ARCHIVE_FOLDER):
            os.mkdir(PASS_FILES_ARCHIVE_FOLDER)

    @staticmethod
    async def write_file(string: str, path: str):
        bytes_content = Fernet(KEY_PHRASE_BYTES).encrypt(string.encode('utf-8'))
        async with open(path, 'wb') as f:
            await f.write(bytes_content)

    @staticmethod
    async def read_file(path: str) -> bytes:
        async with open(path, 'rb') as f:
            return Fernet(KEY_PHRASE_BYTES).decrypt(await f.read())
