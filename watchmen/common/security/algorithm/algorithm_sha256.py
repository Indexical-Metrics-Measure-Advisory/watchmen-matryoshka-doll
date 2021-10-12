from Crypto.Hash import SHA256


def encrypt(value_, params):
    h = SHA256.new()
    h.update(value_.encode('utf-8'))
    return h.hexdigest()
