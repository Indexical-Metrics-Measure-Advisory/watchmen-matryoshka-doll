# from bson import ObjectId as BsonObjectId
from pydantic import BaseModel

from watchmen.entity.data_entity_set import DataEntitySet
# from watchmen.entity.object_id import ObjectIdStr






class DataEntity(BaseModel):
    entityId: str = None
    attr: dict = {}
    # entity_set: DataEntitySet = None
    topicId: str = None
    name: str = None


