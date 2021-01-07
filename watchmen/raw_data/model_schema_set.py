from typing import Dict

from pydantic import BaseModel

from watchmen.raw_data.model_relationship import ModelRelationship
from watchmen.raw_data.model_schema import ModelSchema


class ModelSchemaSet(BaseModel):
    id: int = 0
    code: str = None
    schemas: Dict[str, ModelSchema] = {}
    relationships: Dict[str, ModelRelationship] = {}
