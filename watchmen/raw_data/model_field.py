from enum import Enum
from typing import Optional

from watchmen.common.mongo_model import MongoModel


class FieldType(str, Enum):
    NUM = "num"
    STR = "str"
    DATE = "date"
    time = "time"
    EMAIL = "email"
    ADDR = "address"
    PHONE = "phone"
    IdCard = "IDCard"


class ModelField(MongoModel):
    field_id: int = None
    name: str = None
    description: Optional[str] = None
    type: int = None
    values: list = []
