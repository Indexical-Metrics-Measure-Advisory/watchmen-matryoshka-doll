from datetime import date

from pydantic import BaseModel


class PersonAccessToken(BaseModel):
    patId: str = None
    tokenId: str = None
    userId: str = None
    username: str = None
    tenantId: str = None
    note: str = None
    expired: date = None
    permissions: list = None
