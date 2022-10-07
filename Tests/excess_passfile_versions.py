from Tests.common import *


class TestCryptoUtils(BaseTest):
    @classmethod
    def setUpClass(cls):
        from App.utils.passfile.optimizing import ExcessVersionsFinder
        cls._finder = ExcessVersionsFinder

    def test(self):
        finder = self._finder(2, 2)

        sorted_versions = [  # TODO

        ]

        to_delete = finder.find(sorted_versions)

        self.assertTrue(to_delete)

