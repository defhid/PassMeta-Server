from Tests.common import *
from App.utils.crypto import CryptoUtils


class TestCryptoUtils(BaseTest):
    @classmethod
    def setUpClass(cls):
        cls.crypto_utils = CryptoUtils

    def test_jwt(self):
        origin = {"prop1": 1, "prop2": [1, 2, 3], "prop3": {"sub": True}}

        jwt = self.crypto_utils.make_jwt(origin)

        self.assertTrue(type(jwt) is str)
        self.assertTrue(len(jwt) > 0)

        decoded = self.crypto_utils.read_jwt(jwt)

        self.assertTrue(decoded == origin)

    def test_pwd(self):
        password = "qwerty"

        pwd = self.crypto_utils.make_user_pwd(password)

        self.assertTrue(type(pwd) is str)
        self.assertTrue(len(pwd) > 0)
        self.assertTrue(pwd != password)
        self.assertTrue(pwd == self.crypto_utils.make_user_pwd(password))
        self.assertTrue(self.crypto_utils.check_user_password(password, pwd))

    def test_passfile_encryption(self):
        content = "test content"
        content_bytes = content.encode(encoding='UTF-8')

        encrypted_bytes = self.crypto_utils.encrypt_passfile_smth(content_bytes)

        self.assertTrue(type(encrypted_bytes) is bytes)
        self.assertTrue(len(encrypted_bytes) > 0)
        self.assertTrue(encrypted_bytes != content)

        decrypted_bytes = self.crypto_utils.decrypt_passfile_smth(encrypted_bytes)

        self.assertTrue(type(decrypted_bytes) is bytes)
        self.assertTrue(len(decrypted_bytes) > 0)
        self.assertTrue(decrypted_bytes != encrypted_bytes)
        self.assertTrue(decrypted_bytes == content_bytes)

        decrypted = decrypted_bytes.decode(encoding="UTF-8")

        self.assertTrue(decrypted == content)
