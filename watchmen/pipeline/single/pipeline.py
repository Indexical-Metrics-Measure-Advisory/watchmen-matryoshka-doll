from pydantic import BaseModel


class Trigger(BaseModel):
    type: str = None
    relatedTopicName: str = None


class Pipeline(BaseModel):
    trigger: Trigger = None


