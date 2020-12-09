# from bson import ObjectId as BsonObjectId
from pydantic import BaseModel


class DataEntity(BaseModel):
    entityId: str = None
    attr: dict = {}
    # entity_set: DataEntitySet = None
    topicCode: str = None
    name: str = None


