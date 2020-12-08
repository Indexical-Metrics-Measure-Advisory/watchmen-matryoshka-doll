from pydantic import BaseModel


class FactorGroup(BaseModel):
    groupId: str = None
    name: str = None
