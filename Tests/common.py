import os
from dotenv import load_dotenv
import unittest

__all__ = ('BaseTest',)


load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


class BaseTest(unittest.IsolatedAsyncioTestCase):
    pass
