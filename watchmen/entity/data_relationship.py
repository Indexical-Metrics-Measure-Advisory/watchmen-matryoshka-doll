from pydantic import BaseModel

from watchmen.utils.data_utils import RelationshipType


class DataRelationship(BaseModel):
    code:str=None
    id:str=None
    parent_id:str=None
    child_id:str=None
    type:RelationshipType=None



