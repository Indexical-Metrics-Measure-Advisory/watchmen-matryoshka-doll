from pydantic import BaseModel


class Label(BaseModel):
    id: str = None
    name: str = None
    value: str = None
