from dotenv import load_dotenv
import os
import uvicorn

for env_path in [".env", ".env.local"]:
    load_dotenv(os.path.join(os.path.dirname(__file__), env_path))

from App.app import app
from App.settings import (
    DEBUG,
    LOG_LEVEL,
    UVICORN_HOST,
    UVICORN_PORT,
    UVICORN_PROXY_HEADERS,
    UVICORN_SSL_KEY_FILE,
    UVICORN_SSL_CERT_FILE,
)

def main():
    uvicorn.run(
        app,
        log_level=LOG_LEVEL,
        host=UVICORN_HOST,
        port=UVICORN_PORT,
        proxy_headers=UVICORN_PROXY_HEADERS,
        ssl_keyfile=UVICORN_SSL_KEY_FILE if DEBUG else None,
        ssl_certfile=UVICORN_SSL_CERT_FILE if DEBUG else None,
    )


if __name__ == "__main__":
    main()
