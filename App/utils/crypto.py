__all__ = ('CryptoUtils', )

from App.models.okbad import *
from App.settings import SECRET_KEY_BYTES
from App.utils.logging import LoggerFactory

from typing import Any
from cryptography.fernet import Fernet
import hashlib
import jwt


class CryptoUtils:
    JWT_SECRET_KEY = SECRET_KEY_BYTES.decode('ascii')

    logger = LoggerFactory.get_named("CRYPTO UTILS")

    @classmethod
    def make_jwt(cls, value: dict[str, Any]) -> str:
        return jwt.encode(value, cls.JWT_SECRET_KEY, algorithm='HS256')

    @classmethod
    def read_jwt(cls, value: str) -> dict[str, Any] | None:
        try:
            return jwt.decode(value, cls.JWT_SECRET_KEY, algorithms=['HS256'])
        except Exception as e:
            cls.logger.error("JWT decoding error", e)
            return None

    @classmethod
    def make_user_pwd(cls, raw_password: str) -> str:
        return hashlib.sha512(raw_password.encode('utf-8')).hexdigest()

    @classmethod
    def check_user_password(cls, raw_password: str, pwd: str) -> bool:
        return cls.make_user_pwd(raw_password) == pwd

    @classmethod
    def encrypt_passfile_smth(cls, content: bytes) -> bytes:
        try:
            return Fernet(SECRET_KEY_BYTES).encrypt(content)
        except Exception as e:
            cls.logger.error("Passfile encryption error!", e)
            raise Bad(SERVER_ERR, MORE.info("Server-side encryption failed"))

    @classmethod
    def decrypt_passfile_smth(cls, content: bytes) -> bytes:
        try:
            return Fernet(SECRET_KEY_BYTES).decrypt(content)
        except Exception as e:
            cls.logger.error("Passfile decryption error!", e)
            raise Bad(SERVER_ERR, MORE.info("Server-side decryption failed"))

