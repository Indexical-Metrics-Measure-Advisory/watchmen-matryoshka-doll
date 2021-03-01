from jose import jwt

from watchmen.config.config import settings


def validate_jwt(token):
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    return payload




