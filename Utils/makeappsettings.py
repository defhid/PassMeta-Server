"""
Creates:
  * app_settings.py
"""

from cryptography.fernet import Fernet
from uuid import uuid4
from _common import render_etc, SERVER_DIR
import os


def main():
    filepath = os.path.join(SERVER_DIR, "app_settings.py")
    if os.path.exists(filepath):
        ok = input(f"'{filepath}' already EXISTS! Current app settings may be lost, continue? (Y/n) ").strip()
        if ok != 'Y':
            print("Canceled!")
            return

    app_id = uuid4()
    key_phrase = Fernet.generate_key()

    username = input("Input PostgreSQL username: ").strip()
    password = input(f"Input PostgreSQL password for user '{username}': ").strip()

    render_etc('app-settings', filepath, dict(
        app_id=app_id,
        key_phrase=key_phrase,
        username=username,
        password=password
    ))

    print("Ready!")


if __name__ == '__main__':
    main()
