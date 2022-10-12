from App.database.entities import PassFileVersion
from datetime import datetime, timedelta
from Tests.common import *


class TestCryptoUtils(BaseTest):
    @classmethod
    def setUpClass(cls):
        from App.utils.passfile.optimizing import ExcessVersionsFinder
        cls._finder = ExcessVersionsFinder

    def test_today_versions_1(self):
        finder = self._finder(2, 4)

        sorted_versions = [
            self.make_version(1, 0, 10),
            self.make_version(2, 0, 11),
            self.make_version(3, 0, 12),
            self.make_version(4, 0, 13),
            self.make_version(5, 0, 14),
            self.make_version(6, 0, 15),
        ]

        to_delete = finder.find(sorted_versions)
        to_delete_expect = set(sorted_versions[1:4])

        self.assertTrue(to_delete == to_delete_expect)

    def test_today_versions_2(self):
        finder = self._finder(2, 3)

        sorted_versions = [
            self.make_version(1, 0, 10),
            self.make_version(2, 0, 11),
        ]

        to_delete = finder.find(sorted_versions)

        self.assertTrue(len(to_delete) == 0)

    def test_today_versions_3(self):
        finder = self._finder(2, 1)

        sorted_versions = [
            self.make_version(1, 0, 10),
            self.make_version(2, 0, 11),
        ]

        to_delete = finder.find(sorted_versions)
        to_delete_expect = set(sorted_versions)

        self.assertTrue(to_delete == to_delete_expect)

    def test_previous_versions_1(self):
        finder = self._finder(3, 1)

        sorted_versions = [
            self.make_version(1, -4, 10),
            self.make_version(2, -3, 10),
            self.make_version(3, -2, 10),
            self.make_version(4, -1, 10),
        ]

        to_delete = finder.find(sorted_versions)
        to_delete_expect = {sorted_versions[0]}

        self.assertTrue(to_delete == to_delete_expect)

    def test_previous_versions_2(self):
        finder = self._finder(2, 1)

        sorted_versions = [
            self.make_version(1, -4, 10),
            self.make_version(2, -3, 10),
        ]

        to_delete = finder.find(sorted_versions)

        self.assertTrue(len(to_delete) == 0)

    def test_previous_versions_3(self):
        finder = self._finder(0, 1)

        sorted_versions = [
            self.make_version(1, -4, 10),
            self.make_version(2, -3, 10),
        ]

        to_delete = finder.find(sorted_versions)
        to_delete_expect = set(sorted_versions)

        self.assertTrue(to_delete == to_delete_expect)

    def test_complex_1(self):
        finder = self._finder(2, 2)

        sorted_versions = [
            self.make_version(1, -2, 10),
            self.make_version(2, -2, 11),
            self.make_version(3, -1, 10),
            self.make_version(4, 0, 10),
            self.make_version(5, 0, 11),
            self.make_version(6, 0, 12),
        ]

        to_delete = finder.find(sorted_versions)
        to_delete_expect = {sorted_versions[0], sorted_versions[3], sorted_versions[4]}

        self.assertTrue(to_delete == to_delete_expect)

    def test_complex_2(self):
        finder = self._finder(0, 2)

        sorted_versions = [
            self.make_version(1, -2, 10),
            self.make_version(2, -2, 11),
            self.make_version(3, 0, 10),
            self.make_version(4, 0, 11),
        ]

        to_delete = finder.find(sorted_versions)
        to_delete_expect = set(sorted_versions[:-1])

        self.assertTrue(to_delete == to_delete_expect)

    def test_complex_3(self):
        finder = self._finder(2, 0)

        sorted_versions = [
            self.make_version(1, -2, 10),
            self.make_version(2, -2, 11),
            self.make_version(3, 0, 10),
            self.make_version(4, 0, 11),
        ]

        to_delete = finder.find(sorted_versions)
        to_delete_expect = set(sorted_versions[2:])

        self.assertTrue(to_delete == to_delete_expect)

    def test_complex_4(self):
        finder = self._finder(2, 2)

        sorted_versions = []

        to_delete = finder.find(sorted_versions)

        self.assertTrue(len(to_delete) == 0)

    @staticmethod
    def make_version(version: int, offset_day: int, hour: int) -> PassFileVersion:
        today = datetime.today()

        pfv = PassFileVersion()
        pfv.version = version
        pfv.version_date = today + timedelta(days=offset_day, hours=-today.hour + hour)
        pfv.passfile_id = 1
        return pfv
