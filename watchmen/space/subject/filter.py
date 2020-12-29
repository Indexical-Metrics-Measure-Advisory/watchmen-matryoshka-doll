
from pydantic import BaseModel


class Filter(BaseModel):
    id: int
    key: str
    operator: str
    value: str


