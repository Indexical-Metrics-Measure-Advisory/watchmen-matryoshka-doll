import logging
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from watchmen.auth.service import security
from watchmen.auth.service.user import authenticate
from watchmen.auth.token import Token
from watchmen.auth.user import User
from watchmen.common import deps
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

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.userId, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "role": user.role
    }


@router.post("/login/test-token", response_model=User, tags=["authenticate"])
async def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user

# async def load_user_list_by_names(username_list:List[str],current_user: User = Depends(deps.get_current_user))
#
#
