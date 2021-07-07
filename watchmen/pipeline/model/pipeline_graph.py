from typing import List, Any

from pydantic import BaseModel

from watchmen.common.watchmen_model import WatchmenModel


# class GraphicsPosition(BaseModel):
#     x: float = None
#     y: float = None


class TopicGraphics(BaseModel):
    topicId: str = None
    coordinate: Any = None
    frame: Any = None
    name: Any = None
    rect: Any = None


class PipelinesGraphics(WatchmenModel):
    pipelineGraphId: str = None
    name: str = None
    userId: str = None
    topics: List[TopicGraphics] = []
    tenantId: str = None
