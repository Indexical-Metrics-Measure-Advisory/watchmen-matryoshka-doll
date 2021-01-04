

from pydantic import BaseModel
from typing import Optional


from enum import Enum


class FieldType(str, Enum):
    NUM = "num"
    STR = "str"
    DATE = "date"
    time = "time"
    EMAIL = "email"
    ADDR = "address"
    PHONE = "phone"
    IdCard = "IDCard"


class ModelField(BaseModel):
    field_id: int = None
    name: str = None
    description: Optional[str] = None
    type: int = None
    values: list = []
    # TODO[next] domain field match list

