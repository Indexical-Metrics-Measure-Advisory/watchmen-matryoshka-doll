from pydantic import BaseModel

# from lib.row_data.context import Context
# import ../row_data/ModelSchema
# import lib.row_data.model_schema.ModelSchema
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

    parentName: str = None
    childName: str = None
    # oneToOne: bool= None
    # oneToMany: bool= None


