from base64 import b64encode, b64decode
from typing import Dict

from Crypto.Cipher import AES


def encrypt(value: str, params: Dict):
    obj = AES.new(params.get("key", "hWmZq4t7w9z$C&F)J@NcRfUjXn2r5u8x"), AES.MODE_CFB,
                  params.get("iv", "J@NcRfUjXn2r5u8x"))
    ciphertext = obj.encrypt(value)
    return b64encode(ciphertext).decode()


def decrypt(value: str, params: Dict):
    obj = AES.new(params.get("key", "hWmZq4t7w9z$C&F)J@NcRfUjXn2r5u8x"), AES.MODE_CFB,
                  params.get("iv", "J@NcRfUjXn2r5u8x"))
    return obj.decrypt(b64decode(value)).decode('utf-8')
