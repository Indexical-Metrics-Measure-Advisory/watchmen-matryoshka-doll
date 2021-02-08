from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jsonschema import ValidationError
from starlette import status

from watchmen.auth.storage.user import get_user
from watchmen.auth.user import User
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.config.config import settings

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db():
    return get_client()


def get_current_user(token: str = Depends(reusable_oauth2)
                     ) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

    # token_data = token.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = get_user(payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

