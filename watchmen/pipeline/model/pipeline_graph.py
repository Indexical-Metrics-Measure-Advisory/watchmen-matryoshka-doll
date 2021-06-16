from typing import List, Any

from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel


# class GraphicsPosition(BaseModel):
#     x: float = None
#     y: float = None


class TopicGraphics(BaseModel):
    topicId: str = None
    coordinate: Any = None
    frame: Any = None
    name: Any = None
    rect: Any = None


class PipelinesGraphics(MongoModel):
    pipelineGraphicsId:str = None
    userId: str = None
    topics: List[TopicGraphics] = []
