from watchmen.common.utils.data_utils import RelationshipType
from watchmen.common.watchmen_model import WatchmenModel


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
