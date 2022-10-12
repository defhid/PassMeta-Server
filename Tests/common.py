from App.settings import *
import unittest


def load_test_settings():
    import Tests.app_settings

    load_custom_settings(Tests.app_settings)


load_test_settings()


class BaseTest(unittest.IsolatedAsyncioTestCase):
    pass
