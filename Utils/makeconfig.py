"""
Creates:
  * Gun/service/<GUN_SERVICE_NAME>.service

  * Gun/config/autoload.py
  * Gun/config/manual.py

  * Gun/ssl/config/domain.conf
  * Gun/ssl/config/domain.ext
"""

from _common import render_config, SERVER_DIR, GUN_SERVICE_NAME
import os


def make_dir(*path_components) -> str:
    path = to_path(*path_components)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def to_path(*path_components) -> str:
    return '/'.join(path_components)


def main():
    host = input("Input server host: ").strip().strip('/')
    if not host:
        raise ValueError("Host value is empty!")

    country_code = input("Input 2-chars server Country CODE: ").strip()
    if len(country_code) != 2:
        raise ValueError("Country code is incorrect!")

    folder = make_dir(SERVER_DIR, 'Gun', 'service')
    render_config('gunicorn-service', to_path(folder, f'{GUN_SERVICE_NAME}.service'), dict(
        server_dir=SERVER_DIR
    ))

    folder = make_dir(SERVER_DIR, 'Gun', 'service', 'config')
    render_config('gunicorn-config', to_path(folder, 'autoload.py'), dict(
        server_dir=SERVER_DIR,
        daemon=False
    ))
    render_config('gunicorn-config', to_path(folder, 'manual.py'), dict(
        server_dir=SERVER_DIR,
        daemon=True
    ))

    folder = make_dir(SERVER_DIR, 'Gun', 'ssl', 'config')
    render_config('openssl-config', to_path(folder, 'domain.conf'), dict(
        host=host,
        country_code=country_code
    ))
    render_config('openssl-ext', to_path(folder, 'domain.ext'), dict(
        host=host
    ))

    print("Ready!")


if __name__ == '__main__':
    main()
