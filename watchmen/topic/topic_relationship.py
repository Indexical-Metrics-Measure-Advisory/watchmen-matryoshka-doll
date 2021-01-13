from watchmen.common.mongo_model import MongoModel


class TopicRelationship(MongoModel):
    topicRefId: str = None
    topicId: str = None
    businessKey: str = None
