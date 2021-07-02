from enum import Enum
from typing import Optional, Dict

#
# from watchmen.common.event.event import Event
from watchmen.common.watchmen_model import WatchmenModel
from watchmen.raw_data.context import Context
from watchmen.raw_data.model_field import ModelField
from watchmen.raw_data.model_relationship import ModelRelationship


class Domain(str, Enum):
    INSURANCE = "insurance"


class SubDomain(str, Enum):
    POLICY = "policy"


class ModelSchema(WatchmenModel):
    model_id: str = None
    domain: Domain = None
    subDomain: SubDomain = None
    name: str = None
    description: Optional[str] = None
    context: Optional[Context] = None
    businessFields: Dict[str, ModelField] = {}
    lexiconMatch: list = []
    relationships: Dict[str, ModelRelationship] = {}
    isRoot: bool = False
