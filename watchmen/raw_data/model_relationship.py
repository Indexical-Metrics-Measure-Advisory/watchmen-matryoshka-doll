from watchmen.common.mongo_model import MongoModel
from watchmen.common.utils.data_utils import RelationshipType


class ModelRelationship(MongoModel):
    relationshipId: int = None
    name: str = None
    type: RelationshipType = None
    parentId: str = None
    childId: str = None
    parentName: str = None
    childName: str = None
    parentVariable: dict = {}
    childVariable: dict = {}
