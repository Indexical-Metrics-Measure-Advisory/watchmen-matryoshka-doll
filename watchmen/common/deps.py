from fastapi.exceptions import HTTPException

from fastapi.param_functions import Depends
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from jsonschema import ValidationError
from starlette import status

from watchmen.auth.storage.user import load_user_by_name
from watchmen.auth.user import User, SUPER_ADMIN
from watchmen.common.security.index import validate_jwt
from watchmen.common.security.pat.pat_model import PersonAccessToken
from watchmen.common.security.pat.pat_service import verifyPAT
# from watchmen.common.utils.data_utils import is_superuser
from watchmen.config.config import settings
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel

tokenUrl=f"{settings.API_V1_STR}/login/access-token"
flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": {}})
reusable_oauth2 = OAuth2(
    flows = flows
)


def get_current_user(authorization=Depends(reusable_oauth2)
                     ) -> User:
    scheme, token = get_authorization_scheme_param(authorization)
    username = get_username(scheme, token)
    # if is_superuser(username):
    #     user = User(name=username, role=SUPER_ADMIN)
    # else:
    user = load_user_by_name(username)

    if settings.DEFAULT_DATA_ZONE_ON:
        user.tenantId = "1"

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def get_username(scheme, token):
    if scheme.lower() == "bearer":
        try:
            payload = validate_jwt(token)
        except (jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return payload["sub"]
    elif scheme.lower() == "pat":
        pat: PersonAccessToken = verifyPAT(token)
        if pat is not None:
            return pat.username
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
