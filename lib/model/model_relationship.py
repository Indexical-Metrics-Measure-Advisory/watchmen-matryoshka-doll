from pydantic import BaseModel

# from lib.model.context import Context
# import ../model/ModelSchema
# import lib.model.model_schema.ModelSchema
from enum import Enum


class RelationshipType(Enum):
    OneToOne = "OneToOne"
    OneToMany = "OneToMany"
    ManyToMany = "ManyToMany"


class ModelRelationship(BaseModel):
    relationshipId: int = None
    # fromId: int = None
    # toId : int = None
    type: RelationshipType = None
    modelSchema: BaseModel = None
    # oneToOne: bool= None
    # oneToMany: bool= None


