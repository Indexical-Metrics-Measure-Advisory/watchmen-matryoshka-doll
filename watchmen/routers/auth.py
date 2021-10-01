import logging
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from watchmen.auth.service import security
from watchmen.auth.service.user import authenticate
from watchmen.auth.storage.user import load_user_by_name
from watchmen.auth.token import Token
from watchmen.common.model.user import User
from watchmen.common import deps
from watchmen.common.security.index import validate_jwt
from watchmen.config.config import settings

router = APIRouter()
log = logging.getLogger("app." + __name__)


@router.post("/login/access-token", response_model=Token, tags=["authenticate"])
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()
                             ) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate(form_data.username, form_data.password)
    log.info("login username {0}".format(user.name))
    # print(user)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    result = {
        "access_token": security.create_access_token(
            user.name, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "role": user.role,
        "tenantId": user.tenantId
    }

    return result


@router.get("/login/validate_token", response_model=User, tags=["authenticate"])
async def validate_token(token: str) -> User:
    security_payload = validate_jwt(token)
    user = load_user_by_name(security_payload["sub"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user


@router.post("/login/test-token", response_model=User, tags=["authenticate"])
async def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user

# async def load_user_list_by_names(username_list:List[str],current_user: User = Depends(deps.get_current_user))
#
#
