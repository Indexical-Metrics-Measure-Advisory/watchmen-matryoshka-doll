from typing import Dict

from pydantic import BaseModel

from watchmen.space.row_data import ModelRelationship
from watchmen.space.row_data import ModelSchema


class ModelSchemaSet(BaseModel):
    code:str = None
    schemas: Dict[str,ModelSchema] = {}
    relationships: Dict[str,ModelRelationship] = {}
    # user: str = None
    # insertTime: datetime = None
