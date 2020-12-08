from enum import Enum
from typing import Optional, Dict

from pydantic import BaseModel

from watchmen.event.event import Event
from watchmen.space.row_data.context import Context
from watchmen.space.row_data import ModelField
from watchmen.space.row_data import ModelRelationship


class FieldType(str, Enum):
    NUM = "num"
    STR = "str"
    DATE = "date"
    time = "time"
    EMAIL = "email"
    ADDR = "address"
    PHONE = "phone"
    IdCard = "IDCard"


class Domain(str, Enum):
    INSURANCE = "insurance"


class SubDomain(str, Enum):
    POLICY = "policy"


class ModelSchema(BaseModel):
    modelId: str = None
    event:Event = None
    domain: Domain = None
    subDomain: SubDomain = None
    name: str = None
    description: Optional[str] = None
    context: Optional[Context] = None
    businessFields: Dict[str, ModelField] = {}
    lexiconMatch:list = []
    relationships: Dict[str, ModelRelationship] = {}
    isRoot: bool = False

