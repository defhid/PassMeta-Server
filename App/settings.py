"""
Service default settings.

Requires using load_custom_settings() method before import app,
to load required settings or override default.
"""

import os


DEBUG: bool = False

DB_CONNECTION_STRING: str  # PostgreSQL database connection string
KEY_PHRASE_BYTES: bytes  # Generated key from Fernet.generate_key()


# region SqlAlchemy

DB_CONNECTION_POOL_SIZE: int = 20

# endregion


# region File System

ROOT_DIR: str = os.path.join(*os.path.split(os.path.dirname(os.path.abspath(__file__)))[:-1])

PASSFILES_FOLDER: str = os.path.join(ROOT_DIR, 'Data', 'PassFiles')
PASSFILES_ARCHIVE_FOLDER: str = os.path.join(ROOT_DIR, 'Data', 'PassFilesArchive')

# endregion


# region info

APP_VERSION = "0.9.0"

# endregion


# region Others

SESSION_LIFETIME_DAYS: int = 120

ARCHIVED_PASSFILE_LIFETIME_DAYS: int = 30

OLD_SESSIONS_CHECKING_INTERVAL_MINUTES: int = 60 * 3
OLD_SESSIONS_CHECKING_ON_STARTUP: bool = True

OLD_PASSFILES_CHECKING_INTERVAL_MINUTES: int = 60 * 24
OLD_PASSFILES_CHECKING_ON_STARTUP: bool = True

# endregion


def load_custom_settings(custom_settings):
    required = [
        'DB_CONNECTION_STRING',
        'KEY_PHRASE_BYTES',
    ]

    for name in dir(custom_settings):
        if name.isupper():
            globals()[name] = getattr(custom_settings, name)
            if name in required:
                required.remove(name)

    if required:
        raise ImportError(f"Required custom settings not found! ({', '.join(required)})")
