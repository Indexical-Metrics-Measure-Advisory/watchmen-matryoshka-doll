
from pydantic import BaseModel


class DataEntity(BaseModel):
    entity_id: str = None
    name: str = None
    attrs: list = []


class Attribute(BaseModel):
    name: str
    type: int
    values:list=[]

