"""
Service default settings.

Requires using load_custom_settings() method before import app,
to load required settings or override default.
"""

import os as __os


# region Common

APP_VERSION = "2.0.0"
APP_ID: str  # [REQUIRED]: Unique PassMeta server identifier

SECRET_KEY_BYTES: bytes  # [REQUIRED]: Generated key from Fernet.generate_key()

DEBUG: bool = False

# endregion


# region Database

DB_CONNECTION: dict  # [REQUIRED]: PostgreSQL database connection setup: host, port, user, password, database etc.
DB_CONNECTION_POOL_MIN_SIZE: int = 10
DB_CONNECTION_POOL_MAX_SIZE: int = 30

# endregion


# region File System

ROOT_DIR: str = __os.path.join(*__os.path.split(__os.path.dirname(__os.path.abspath(__file__)))[:-1])

PASSFILES_FOLDER: str = __os.path.join(ROOT_DIR, 'Data', 'PassFiles')

# endregion


# region Others

SESSION_LIFETIME_DAYS: int = 120  # how long to keep user's web session

PASSFILE_KEEP_DAY_VERSIONS: int = 3  # max number of stored file versions, in scope of current day
PASSFILE_KEEP_VERSIONS: int = 5  # max number of stored file versions, excluding scope of current day

HISTORY_KEEP_MONTHS: int = 12  # how many months to store history

OLD_HISTORY_CHECKING_INTERVAL_DAYS: int = 30  # how often to check old history more info
OLD_HISTORY_CHECKING_ON_STARTUP: bool = True  # launch checking old history more info on application startup

CHECK_MIGRATIONS_ON_STARTUP: bool = True  # find and execute new database migrations

# endregion


def load_custom_settings(custom_settings):
    required = [
        'APP_ID',
        'DB_CONNECTION',
        'SECRET_KEY_BYTES',
    ]

    missed = [
        'APP_VERSION',
        'ROOT_DIR',
    ]

    for name in dir(custom_settings):
        if name.isupper():
            globals()[name] = getattr(custom_settings, name)
            if name in required and name not in missed:
                required.remove(name)

    if required:
        raise ImportError(f"Required custom settings not found! ({', '.join(required)})")
