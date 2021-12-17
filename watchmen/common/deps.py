from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.param_functions import Depends
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt
from jsonschema import ValidationError
from model.model.common.user import User
from starlette import status

from watchmen.auth.storage.user import load_user_by_name
from watchmen.common.security.index import validate_jwt
from watchmen.common.security.pat.pat_model import PersonAccessToken
from watchmen.common.security.pat.pat_service import verifyPAT
from watchmen.config.config import settings

tokenUrl = f"{settings.API_V1_STR}/login/access-token"
flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": {}})
reusable_oauth2 = OAuth2(
    flows=flows
)


def get_current_user(authorization=Depends(reusable_oauth2)
                     ) -> User:
    scheme, token = get_authorization_scheme_param(authorization)
    username = get_username(scheme, token)

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
