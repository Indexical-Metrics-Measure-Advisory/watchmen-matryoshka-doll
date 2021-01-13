from typing import Dict

from watchmen.common.mongo_model import MongoModel
from watchmen.raw_data.model_relationship import ModelRelationship
from watchmen.raw_data.model_schema import ModelSchema


class ModelSchemaSet(MongoModel):
    id: int = 0
    code: str = None
    schemas: Dict[str, ModelSchema] = {}
    relationships: Dict[str, ModelRelationship] = {}
