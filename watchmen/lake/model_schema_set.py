from typing import List,Dict

from pydantic import BaseModel

from watchmen.lake.model_relationship import ModelRelationship
from watchmen.lake.model_schema import ModelSchema


class ModelSchemaSet(BaseModel):
    schemas: Dict[str,ModelSchema] = {}
    relationships: Dict[str,ModelRelationship] = {}
