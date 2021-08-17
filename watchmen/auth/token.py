from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    tenantId: str = None


class TokenPayload(BaseModel):
    sub: Optional[int] = None
