from enum import Enum
from typing import Optional, Dict

from pydantic import BaseModel

from lib.model.context import Context
from lib.model.model_field import ModelField
from lib.model.model_relationship import ModelRelationship


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
    modelId: int = None
    domain: Domain = None
    subDomain: SubDomain = None
    name: str = None
    description: Optional[str] = None
    context: Optional[Context] = None
    businessFields: Dict[str, ModelField] = {}
    lexiconMatch:list = []
    relationships: Dict[str, ModelRelationship] = {}
