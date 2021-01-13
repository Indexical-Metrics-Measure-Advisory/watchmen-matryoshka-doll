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


@router.post("/login/access-token", response_model=Token, tags=["authenticate"])
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()
                       ) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = authenticate(form_data.username, form_data.password)

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
    }


@router.post("/login/test-token", response_model=User, tags=["authenticate"])
def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    return current_user

# @router.post("/password-recovery/{email}", response_model=schemas.Msg)
# def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
#     """
#     Password Recovery
#     """
#     user = crud.user.get_by_email(db, email=email)
#
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this username does not exist in the system.",
#         )
#     password_reset_token = generate_password_reset_token(email=email)
#     send_reset_password_email(
#         email_to=user.email, email=email, token=password_reset_token
#     )
#     return {"msg": "Password recovery email sent"}
#
#
# @router.post("/reset-password/", response_model=schemas.Msg)
# def reset_password(
#     token: str = Body(...),
#     new_password: str = Body(...),
#     db: Session = Depends(deps.get_db),
# ) -> Any:
#     """
#     Reset password
#     """
#     email = verify_password_reset_token(token)
#     if not email:
#         raise HTTPException(status_code=400, detail="Invalid token")
#     user = crud.user.get_by_email(db, email=email)
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this username does not exist in the system.",
#         )
#     elif not crud.user.is_active(user):
#         raise HTTPException(status_code=400, detail="Inactive user")
#     hashed_password = get_password_hash(new_password)
#     user.hashed_password = hashed_password
#     db.add(user)
#     db.commit()
#     return {"msg": "Password updated successfully"}
