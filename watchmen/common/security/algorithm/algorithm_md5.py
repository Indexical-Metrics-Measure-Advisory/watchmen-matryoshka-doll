import hashlib
from base64 import b64encode


def encrypt(value_, params):
    md5 = hashlib.md5(value_.encode('utf-8')).digest()
    return b64encode(md5).decode()
