from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jsonschema import ValidationError
from starlette import status
from starlette.requests import Request

from watchmen.auth.storage.user import load_user_by_name
from watchmen.auth.user import User, SUPER_ADMIN
from watchmen.common.security.index import validate_jwt
from watchmen.common.security.pat.pat_model import PersonAccessToken
from watchmen.common.security.pat.pat_service import verifyPAT
from watchmen.common.utils.data_utils import is_superuser
from watchmen.config.config import settings

'''
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_current_user(token: str = Depends(reusable_oauth2)
                     ) -> User:
    try:
        payload = validate_jwt(token)

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

    if settings.DEFAULT_DATA_ZONE_ON:
        user.tenantId="1"

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
'''


def get_current_user(request: Request) -> User:
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        scheme, param = "", ""
    else:
        scheme, _, param = authorization.partition(" ")
    if not authorization or (scheme.lower() != "bearer" and scheme.lower() != "pat"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = param
    if scheme.lower() == "bearer":
        try:
            payload = validate_jwt(token)
        except (jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        username = payload["sub"]
    elif scheme.lower() == "pat":
        pat: PersonAccessToken = verifyPAT(token)
        if pat is not None:
            username = pat.username
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
    if is_superuser(username):
        user = User(name=username, role=SUPER_ADMIN)
    else:
        user = load_user_by_name(username)

    if settings.DEFAULT_DATA_ZONE_ON:
        user.tenantId = "1"

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
