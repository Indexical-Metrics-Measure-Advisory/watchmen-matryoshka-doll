from typing import List

from pydantic import BaseModel

from watchmen.schema.model_relationship import ModelRelationship
from watchmen.schema.model_schema import ModelSchema


class ModelSchemaSet(BaseModel):
    schemas: List[ModelSchema] = []
    relationships: List[ModelRelationship] = []
