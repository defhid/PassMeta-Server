from App.database.entities import PassFileVersion
from Tests.common import *

from datetime import datetime
import os


class TestPassFileUtils(BaseTest):
    @classmethod
    def setUpClass(cls):
        from App.utils.passfile.files import PassFileUtils
        cls.utils = PassFileUtils

    async def test(self):
        self.utils.ensure_folders_created()

        pfv = self.make_version(1, 123)
        content = b"TEST CONTENT"

        await self.utils.write_file(pfv, content)

        path = self.utils.get_filepath(pfv)

        self.assertTrue(os.path.exists(path))

        pfv_check = self.make_version(1, 123)
        content_check = await self.utils.read_file(pfv_check)

        self.assertTrue(content == content_check)

        self.utils.delete_file(pfv)

        self.assertFalse(os.path.exists(path))

    @staticmethod
    def make_version(version: int, user_id: int) -> PassFileVersion:
        pfv = PassFileVersion()
        pfv.version = version
        pfv.version_date = datetime.today()
        pfv.passfile_id = 1
        pfv.user_id = user_id
        return pfv
