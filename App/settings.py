"""
Application settings.
"""
from logging import getLevelNamesMapping as __getLevelNamesMapping, WARNING as __warning
import App.utils.settings as __resolve


""" Version of PassMeta server application
"""
APP_VERSION = "2.0.1"

""" Unique identifier of PassMeta server application
"""
APP_ID = __resolve.string("APP_ID", required=True)

""" Secret key for storage encryption (generated from Fernet.generate_key)
"""
APP_SECRET_KEY_BYTES = __resolve.string("APP_SECRET_KEY", required=True).encode("utf-8")

""" Debug mode
"""
DEBUG = __resolve.boolean("DEBUG", default=False)

""" Logging level (FATAL, WARNING, INFO, DEBUG)
"""
LOG_LEVEL = __getLevelNamesMapping().get(__resolve.string("APP_LOG_LEVEL", default="WARNING").upper(), __warning)

""" Path to logs directory
"""
LOG_FOLDER = __resolve.string("APP_LOG_FOLDER", default=None)


""" Host to listen
"""
UVICORN_HOST = __resolve.string("UVICORN_HOST", required=True)

""" Port to listen
"""
UVICORN_PORT = __resolve.integer("UVICORN_PORT", required=True)

""" Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info
"""
UVICORN_PROXY_HEADERS = __resolve.boolean("UVICORN_PROXY_HEADERS", default=False)

""" Url pattern for cross-origin requests
"""
UVICORN_CORS_PATTERN = __resolve.string("UVICORN_CORS_PATTERN", default=False)

""" Path to SSL key (dev only)
"""
UVICORN_SSL_KEY_FILE = __resolve.string("UVICORN_SSL_KEY_FILE", default=None) if UVICORN_PORT == 443 else None

""" Path to SSL certificate (dev only)
"""
UVICORN_SSL_CERT_FILE = __resolve.string("UVICORN_SSL_CERT_FILE", default=None) if UVICORN_PORT == 443 else None


""" PostgreSQL database connection setup
"""
DB_CONNECTION = {
    'host': __resolve.string("DB_CONNECTION__HOST", required=True),
    'port': __resolve.integer("DB_CONNECTION__PORT", required=True),
    'user': __resolve.string("DB_CONNECTION__USER", required=True),
    'password': __resolve.string("DB_CONNECTION__PASSWORD", required=True),
    'database': __resolve.string("DB_CONNECTION__DATABASE", required=True),
    'command_timeout': __resolve.integer("DB_CONNECTION__TIMEOUT", default=30)
}

""" Database connection pool min size
"""
DB_CONNECTION_POOL_MIN_SIZE: int = 10

""" Database connection pool max size
"""
DB_CONNECTION_POOL_MAX_SIZE: int = 30


""" How long to keep user's web session
"""
SESSION_LIFETIME_DAYS = __resolve.integer("SESSION_LIFETIME_DAYS", default=120)

""" Path to passfiles directory
"""
PASSFILES_FOLDER = __resolve.path("PASSFILES_FOLDER", required=True)

""" Max number of stored file versions, in scope of current day
"""
PASSFILE_KEEP_DAY_VERSIONS = __resolve.integer("PASSFILE_KEEP_DAY_VERSIONS", default=3)

""" Max number of stored file versions, excluding scope of current day
"""
PASSFILE_KEEP_VERSIONS = __resolve.integer("PASSFILE_KEEP_VERSIONS", default=5)

""" How many months to store history
"""
HISTORY_KEEP_MONTHS = __resolve.integer("HISTORY_KEEP_MONTHS", default=24)

""" How often to check old history more info
"""
HISTORY_CHECKING_INTERVAL_DAYS = __resolve.integer("HISTORY_CHECKING_INTERVAL_DAYS", default=30)

""" Launch checking old history more info on application startup
"""
CHECK_HISTORY_ON_STARTUP = __resolve.boolean("CHECK_HISTORY_ON_STARTUP", default=True)

""" find and execute new database migrations
"""
CHECK_MIGRATIONS_ON_STARTUP = __resolve.boolean("CHECK_MIGRATIONS_ON_STARTUP", default=True)
