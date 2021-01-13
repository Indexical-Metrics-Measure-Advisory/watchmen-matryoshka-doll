from fastapi import HTTPException

from watchmen.auth.service.security import verify_password
from watchmen.auth.storage.user import load_user_by_name
from watchmen.auth.user import User


def get_current_user():
    pass


def check_promise(current_user):
    pass


def authenticate(username, password):
    user = load_user_by_name(username)
    if user is None:
        raise HTTPException(401)
    else:
        user = User.parse_obj(user)
        if verify_password(password, user.password):
            return User.parse_obj(user)
        else:
            raise HTTPException(401)
