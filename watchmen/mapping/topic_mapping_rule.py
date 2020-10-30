from pydantic import BaseModel


class TopicMappingRule(BaseModel):
    topicMappingId: str = None
    targetTopicId: str = None
    lakeSchemaId: str = None








