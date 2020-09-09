from pydantic import BaseModel

# from lib.schema.context import Context
# import ../schema/ModelSchema
# import lib.schema.model_schema.ModelSchema
from watchmen.utils.data_utils import RelationshipType


class ModelRelationship(BaseModel):
    name:str = None
    relationshipId: int = None
    # fromId: int = None
    # toId : int = None
    type: RelationshipType = None
    # modelSchema: BaseModel = None
    parentId: str = None
    childId:str = None
    parentVariable:dict={}
    childVariable: dict = {}
    # oneToOne: bool= None
    # oneToMany: bool= None


