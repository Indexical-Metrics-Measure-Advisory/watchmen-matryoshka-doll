from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jsonschema import ValidationError
from starlette import status

from watchmen.auth.storage.user import load_user_by_name
from watchmen.auth.user import User, SUPER_ADMIN
from watchmen.common.security.index import validate_jwt
from watchmen.common.utils.data_utils import is_superuser
from watchmen.config.config import settings

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_current_user(token: str = Depends(reusable_oauth2)
                     ) -> User:
    try:
        print("token", token)
        payload = validate_jwt(token)

        print("payload", payload)

    # token_data = token.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    username = payload["sub"]
    if is_superuser(username):
        user = User(name=username, role=SUPER_ADMIN)
    else:
        user = load_user_by_name(username)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
