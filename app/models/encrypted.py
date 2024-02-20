from __future__ import annotations
from typing import Self

from Crypto.Cipher import AES


class EncryptedString:
    @staticmethod
    def decrypt(secret_key: bytes, data: str) -> str:
        if '|' not in data:
            raise ValueError("Invalid encrypted string")
        
        secret, iv = data.split("|")

        cipher = AES.new(
            secret_key,
            AES.MODE_CFB,
            iv=bytes.fromhex(iv),
        )

        return cipher.decrypt(
            bytes.fromhex(
                secret
            )
        ).decode("utf-8")
    
    @staticmethod
    def encrypt(secret_key: bytes, data: str | bytes) -> str:
        cipher = AES.new(
            secret_key,
            AES.MODE_CFB,
        )

        if isinstance(data, str):
            data = data.encode("utf-8")
        
        cipher_text: bytes = cipher.encrypt(data)
        iv: bytes = cipher.iv

        return f"{cipher_text.hex()}|{iv.hex()}"