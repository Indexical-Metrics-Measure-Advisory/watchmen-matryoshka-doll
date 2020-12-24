from pydantic import BaseModel

# from watchmen.entity.object_id import PydanticObjectId
from watchmen.common.utils.data_utils import RelationshipType


class DataRelationship(BaseModel):
    desc:str=None
    id:str=None
    parentId:str=None
    childId:str=None
    type:RelationshipType=None
    name:str=None






