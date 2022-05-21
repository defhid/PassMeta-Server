from App.settings import SECRET_KEY_BYTES
from App.special import *
from App.utils.logging import Logger

from cryptography.fernet import Fernet
import hashlib
import jwt

__all__ = (
    'CryptoUtils',
)


logger = Logger(__file__)


class CryptoUtils:
    JWT_SECRET_KEY = SECRET_KEY_BYTES.decode('ascii')

    @classmethod
    def make_jwt(cls, value: Dict[str, Any]) -> str:
        return jwt.encode(value, cls.JWT_SECRET_KEY, algorithm='HS256')

    @classmethod
    def read_jwt(cls, value: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(value, cls.JWT_SECRET_KEY, algorithms=['HS256'])
        except Exception as e:
            logger.error("JWT decoding error", e)
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
            logger.error("Passfile encryption error!", e)
            raise Bad(None, UNKNOWN_ERR, MORE.text("Server-side encryption failed"))

    @classmethod
    def decrypt_passfile_smth(cls, content: bytes) -> bytes:
        try:
            return Fernet(SECRET_KEY_BYTES).decrypt(content)
        except Exception as e:
            logger.error("Passfile decryption error!", e)
            raise Bad(None, UNKNOWN_ERR, MORE.text("Server-side decryption failed"))

