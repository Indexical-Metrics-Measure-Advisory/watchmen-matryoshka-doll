
from pydantic import BaseModel
from watchmen.space.factor.factor import Factor


class Filter(BaseModel):
    id: int
    key: str
    operator: str
    value: str


