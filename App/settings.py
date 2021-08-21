import os


def load_private_settings(private_settings):
    global DEBUG, DB_CONNECTION_STRING, KEY_PHRASE_BYTES

    DEBUG = private_settings.DEBUG
    DB_CONNECTION_STRING = private_settings.DB_CONNECTION_STRING
    KEY_PHRASE_BYTES = private_settings.KEY_PHRASE_BYTES


DEBUG: bool
DB_CONNECTION_STRING: str  # PostgreSQL database connection string
KEY_PHRASE_BYTES: bytes  # Generated key from Fernet.generate_key()


# region SqlAlchemy

DB_CONNECTION_POOL_SIZE = 20

# endregion


# region File System

ROOT_DIR = os.path.join(*os.path.split(os.path.dirname(os.path.abspath(__file__)))[:-1])

PASSFILES_FOLDER = os.path.join(ROOT_DIR, 'Data', 'PassFiles')
PASSFILES_ARCHIVE_FOLDER = os.path.join(ROOT_DIR, 'Data', 'PassFilesArchive')

# endregion


# region Others

SESSION_LIFETIME_DAYS = 120

ARCHIVED_PASSFILE_LIFETIME_DAYS = 30

OLD_SESSIONS_CHECKING_INTERVAL_MINUTES = 60 * 3
OLD_SESSIONS_CHECKING_ON_STARTUP = True

OLD_PASSFILES_CHECKING_INTERVAL_MINUTES = 60 * 24
OLD_PASSFILES_CHECKING_ON_STARTUP = True

# endregion
