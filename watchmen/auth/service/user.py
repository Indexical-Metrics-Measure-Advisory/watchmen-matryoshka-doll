from fastapi import HTTPException, Depends
from starlette import status

from watchmen.auth.service.security import verify_password
from watchmen.auth.storage.user import load_user_by_name
from watchmen.auth.user import User
from watchmen.common import deps


def authenticate(username, password):
    user = load_user_by_name(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        user = User.parse_obj(user)
        if verify_password(password, user.password):
            return User.parse_obj(user)
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def __is_initialized(db=Depends(deps.get_db)):
    pass
    # db.get_connection


def init_superuser():
    pass

    if __is_initialized():
        pass
