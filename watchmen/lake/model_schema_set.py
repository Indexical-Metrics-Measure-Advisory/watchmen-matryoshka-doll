import datetime
from typing import Dict

from pydantic import BaseModel

from watchmen.lake.model_relationship import ModelRelationship
from watchmen.lake.model_schema import ModelSchema


class ModelSchemaSet(BaseModel):
    code:str = None
    schemas: Dict[str,ModelSchema] = {}
    relationships: Dict[str,ModelRelationship] = {}
    # user: str = None
    # insertTime: datetime = None
