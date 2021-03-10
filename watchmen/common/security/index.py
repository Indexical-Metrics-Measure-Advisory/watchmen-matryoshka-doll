from fastapi import HTTPException
from jose import jwt
from jsonschema import ValidationError
from starlette import status

from watchmen.config.config import settings


def validate_jwt(token):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
