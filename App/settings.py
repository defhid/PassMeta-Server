import os

# noinspection PyUnresolvedReferences
from .private import (
    DB_CONNECTION_STRING,  # PostgreSQL database connection string
    KEY_PHRASE_BYTES,  # Generated key from Fernet.generate_key()
)

DEBUG = True

# region SqlAlchemy

DB_CONNECTION_POOL_SIZE = 20

# endregion

# region File System

ROOT_DIR = os.path.join(*os.path.split(os.path.dirname(os.path.abspath(__file__)))[:-1])

PASSFILES_FOLDER = os.path.join(ROOT_DIR, "PassFiles")
PASSFILES_ARCHIVE_FOLDER = os.path.join(ROOT_DIR, "PassFilesArchive")

# endregion

# region Others

SESSION_LIFETIME_DAYS = 120

ARCHIVED_PASSFILE_LIFETIME_DAYS = 30

# endregion
