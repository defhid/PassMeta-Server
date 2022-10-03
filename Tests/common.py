import unittest


def load_test_settings():
    from App.settings import load_custom_settings
    import app_test_settings

    load_custom_settings(app_test_settings)


load_test_settings()


class BaseTest(unittest.TestCase):
    pass
