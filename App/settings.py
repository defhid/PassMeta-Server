"""
Service default settings.

Requires using load_custom_settings() method before import app,
to load required settings or override default.
"""

import os


# region Common

APP_VERSION = "0.9.0"

DEBUG: bool = False

# endregion


# region Database

DB_CONNECTION: dict  # PostgreSQL database connection setup: host, port, user, password, database etc.
DB_CONNECTION_POOL_MIN_SIZE: int = 10
DB_CONNECTION_POOL_MAX_SIZE: int = 30

# endregion


# region File System

ROOT_DIR: str = os.path.join(*os.path.split(os.path.dirname(os.path.abspath(__file__)))[:-1])

PASSFILES_FOLDER: str = os.path.join(ROOT_DIR, 'Data', 'PassFiles')

PASSFILES_ENCODING = "UTF-8"

KEY_PHRASE_BYTES: bytes  # Generated key from Fernet.generate_key()

# endregion


# region Others

SESSION_LIFETIME_DAYS: int = 120  # how long to keep user web session

SESSION_CACHE_SIZE: int = 200  # limit on the number of cached sessions

PASSFILE_KEEP_VERSIONS: int = 3  # max number of stored file versions

HISTORY_KEEP_MONTHS: int = 12  # how many last months to store history more info (the origin history is permanent)

OLD_SESSIONS_CHECKING_INTERVAL_MINUTES: int = 60 * 3  # how often to check old user web sessions
OLD_SESSIONS_CHECKING_ON_STARTUP: bool = True  # launch checking old user web sessions on application startup

OLD_HISTORY_CHECKING_INTERVAL_DAYS: int = 30  # how often to check old history more info
OLD_HISTORY_CHECKING_ON_STARTUP: bool = True  # launch checking old history more info on application startup

CHECK_DATABASE_ON_SATRTUP: bool = True  # ensure all db models exist, create if required

# endregion


def load_custom_settings(custom_settings):
    required = [
        'DB_CONNECTION',
        'KEY_PHRASE_BYTES',
    ]

    for name in dir(custom_settings):
        if name.isupper():
            globals()[name] = getattr(custom_settings, name)
            if name in required:
                required.remove(name)

    if required:
        raise ImportError(f"Required custom settings not found! ({', '.join(required)})")
