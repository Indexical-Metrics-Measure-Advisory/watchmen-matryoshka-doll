from datetime import date

from pydantic import BaseModel


class PersonAccessToken(BaseModel):
    pat_id: str = None
    token_id: str = None
    user_id: str = None
    tenant_id: str = None
    note: str = None
    expired: date = None
    permissions: list = None
