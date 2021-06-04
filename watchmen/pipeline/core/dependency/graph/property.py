from pydantic import BaseModel


class Property(BaseModel):
    id: str = None
    name: str = None
    value: str = None
