from typing import List

from pydantic import BaseModel

from watchmen.lake.model_relationship import ModelRelationship
from watchmen.lake.model_schema import ModelSchema


class ModelSchemaSet(BaseModel):
    schemas: List[ModelSchema] = []
    relationships: List[ModelRelationship] = []
