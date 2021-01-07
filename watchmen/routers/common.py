from fastapi import APIRouter

from watchmen.topic.storage.topic_schema_storage import save_topic, get_topic_by_id, get_topic_by_name
from watchmen.topic.topic import Topic

router = APIRouter()


# @router.post("/login/access-token", response_model=Token)
# def login_access_token(
#    client = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
# ) -> Any:
#     """
#     OAuth2 compatible token login, get an access token for future requests
#     """
#     user = authenticate(client,form_data.username,form_data.password)
#
#     if not user:
#         raise HTTPException(status_code=400, detail="Incorrect email or password")
#     elif not user.is_active:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     return {
#         "access_token": security.create_access_token(
#             user.id, expires_delta=access_token_expires
#         ),
#         "token_type": "bearer",
#     }
#
#
# @router.post("/login/test-token", response_model=User)
# def test_token(current_user: User = Depends(deps.get_current_user)) -> Any:
#     """
#     Test access token
#     """
#     return current_user
#
#
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


@router.get("/health")
async def health():
    return {"health": True}


async def save_topic_http(topic: Topic):
    return save_topic(topic)


async def load_topic(topic_id: str):
    return get_topic_by_id(topic_id)


async def save_topic_relationship(topic_relationship):
    pass


async def load_topic_by_name_http(topic_name: str):
    return get_topic_by_name(topic_name)


async def fuzzy_query_topic(topic_name: str):
    pass


async def fuzzy_query_factor(factor_name: str):
    pass
