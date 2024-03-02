from __future__ import annotations
import hashlib

from Crypto.Cipher import AES


class Encrypted:
    def __init__(self, secret_key: bytes) -> None:
        self.secret_key = secret_key
    
    def decrypt(self, data: str) -> str:
        if '|' not in data:
            raise ValueError("Invalid encrypted string")
        
        secret, iv = data.split("|")

        cipher = AES.new(
            self.secret_key,
            AES.MODE_CFB,
            iv=bytes.fromhex(iv),
        )

        return cipher.decrypt(
            bytes.fromhex(
                secret
            )
        ).decode("utf-8")
    
    def encrypt(self, data: str | bytes) -> str:
        cipher = AES.new(
            self.secret_key,
            AES.MODE_CFB,
        )

        if isinstance(data, str):
            data = data.encode("utf-8")
        
        cipher_text: bytes = cipher.encrypt(data)
        iv: bytes = cipher.iv

        return f"{cipher_text.hex()}|{iv.hex()}"

    @staticmethod
    def hash(data: str) -> str:
        return hashlib.sha256(
            data.encode(
                "utf-8"
            )
        ).hexdigest()
