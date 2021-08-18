import os

# noinspection PyUnresolvedReferences
from .private import (
    DB_CONNECTION_STRING,
    KEY_PHRASE_BYTES,
)

DEBUG = True

SESSION_LIFETIME_DAYS = 1

DB_CONNECTION_POOL_SIZE = 20

ROOT_DIR = os.path.join(*os.path.split(os.path.dirname(os.path.abspath(__file__)))[:-1])

PASS_FILES_FOLDER = os.path.join(ROOT_DIR, "PassFiles")
PASS_FILES_ARCHIVE_FOLDER = os.path.join(ROOT_DIR, "PassFilesArchive")
