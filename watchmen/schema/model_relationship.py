from pydantic import BaseModel

# from lib.schema.context import Context
# import ../schema/ModelSchema
# import lib.schema.model_schema.ModelSchema
from enum import Enum


class RelationshipType(Enum):
    OneToOne = "OneToOne"
    OneToMany = "OneToMany"
    ManyToMany = "ManyToMany"


class ModelRelationship(BaseModel):
    name:str = None
    relationshipId: int = None
    # fromId: int = None
    # toId : int = None
    type: RelationshipType = None
    # modelSchema: BaseModel = None
    parentId: int = None
    childId:int = None
    parentVariable:dict={}
    childVariable: dict = {}
    # oneToOne: bool= None
    # oneToMany: bool= None


