from pydantic import BaseModel


class TopicRelationship(BaseModel):
    topicRefId: str = None
    topicId: str = None
    businessKey: str = None
