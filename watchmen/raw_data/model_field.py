from enum import Enum
from typing import Optional

from model.model.common.watchmen_model import WatchmenModel


class FieldType(str, Enum):
    NUM = "num"
    STR = "str"
    DATE = "date"
    time = "time"
    EMAIL = "email"
    ADDR = "address"
    PHONE = "phone"
    IdCard = "IDCard"


class ModelField(WatchmenModel):
    field_id: int = None
    name: str = None
    description: Optional[str] = None
    type: str = None
    values: list = []
