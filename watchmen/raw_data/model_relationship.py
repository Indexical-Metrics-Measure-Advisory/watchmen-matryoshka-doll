from watchmen.common.watchmen_model import WatchmenModel
from watchmen.common.utils.data_utils import RelationshipType


class ModelRelationship(WatchmenModel):
    relationshipId: int = None
    name: str = None
    type: RelationshipType = None
    parentId: str = None
    childId: str = None
    parentName: str = None
    childName: str = None
    parentVariable: dict = {}
    childVariable: dict = {}
