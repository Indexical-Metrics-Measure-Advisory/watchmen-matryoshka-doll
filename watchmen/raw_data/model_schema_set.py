from typing import Dict

from model.model.common.watchmen_model import WatchmenModel

from watchmen.raw_data.model_relationship import ModelRelationship
from watchmen.raw_data.model_schema import ModelSchema


class ModelSchemaSet(WatchmenModel):
    id: int = 0
    code: str = None
    schemas: Dict[str, ModelSchema] = {}
    relationships: Dict[str, ModelRelationship] = {}
