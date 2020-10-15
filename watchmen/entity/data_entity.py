# from bson import ObjectId as BsonObjectId
from pydantic import BaseModel

from watchmen.entity.data_entity_set import DataEntitySet


class DataEntity(BaseModel):
    entityId: str = None
    attr: dict = {}
    # entity_set: DataEntitySet = None
    topicCode: str = None
    name: str = None


