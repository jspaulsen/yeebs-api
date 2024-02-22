import secrets

from Crypto.Cipher import AES
import pytest

from app.models.encrypted import Encrypted


@pytest.fixture
def generate_secret_key():
    return secrets.token_bytes(16)


class TestEncryptedString:
    def test_encrypt(self, generate_secret_key):
        secret_key = generate_secret_key
        data = "this is a test data string"
        encrypt = Encrypted(secret_key)

        encrypted = encrypt.encrypt(data)

        assert '|' in encrypted

        secret, iv = encrypted.split("|")

        # decrypt the data and compare
        crypt = AES.new(
            secret_key,
            AES.MODE_CFB,
            iv=bytes.fromhex(iv),
        )

        decrypted = crypt.decrypt(
            bytes.fromhex(secret)
        ).decode("utf-8")

        assert decrypted == data
    
    def test_decrypt(self, generate_secret_key):
        secret_key = generate_secret_key
        data = "this is a test data string"
        encrypt = Encrypted(secret_key)

        encrypted = encrypt.encrypt(data)
        decrypted = encrypt.decrypt(encrypted)

        assert decrypted == data