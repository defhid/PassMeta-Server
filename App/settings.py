import os

# noinspection PyUnresolvedReferences
from .settings_private import (
    DB_CONNECTION_STRING,  # PostgreSQL database connection string
    KEY_PHRASE_BYTES,  # Generated key from Fernet.generate_key()
)

DEBUG = False


# region SqlAlchemy

DB_CONNECTION_POOL_SIZE = 20

# endregion


# region File System

ROOT_DIR = os.path.join(*os.path.split(os.path.dirname(os.path.abspath(__file__)))[:-1])

PASSFILES_FOLDER = os.path.join(ROOT_DIR, 'data', 'PassFiles')
PASSFILES_ARCHIVE_FOLDER = os.path.join(ROOT_DIR, 'data', 'PassFilesArchive')

# endregion


# region Others

SESSION_LIFETIME_DAYS = 120

ARCHIVED_PASSFILE_LIFETIME_DAYS = 30

OLD_SESSIONS_CHECKING_INTERVAL_MINUTES = 60 * 3
OLD_SESSIONS_CHECKING_ON_STARTUP = True

OLD_PASSFILES_CHECKING_INTERVAL_MINUTES = 60 * 24
OLD_PASSFILES_CHECKING_ON_STARTUP = True

# endregion
