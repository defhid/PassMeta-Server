from App.settings import *
import unittest


def load_test_settings():
    import app_test_settings

    load_custom_settings(app_test_settings)


load_test_settings()


class BaseTest(unittest.TestCase):
    pass
