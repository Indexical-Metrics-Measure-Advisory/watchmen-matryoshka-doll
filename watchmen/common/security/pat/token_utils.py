import secrets


def create_token():
    token = secrets.token_urlsafe(16)
    return token
