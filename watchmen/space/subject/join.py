from pydantic import BaseModel


class Join(BaseModel):
    id: int
    left: str
    right: str
    key: str
