from typing import List, Any

from pydantic import BaseModel

from watchmen.common.watchmen_model import WatchmenModel


class ConnectedSpaceBlockGraphics(BaseModel):
    rect: Any = None


class TopicGraphics(ConnectedSpaceBlockGraphics):
    topicId: str = None


class SubjectGraphics(ConnectedSpaceBlockGraphics):
    subjectId: str = None


class ConnectedSpaceGraphics(WatchmenModel):
    connectId: str = None
    topics: List[TopicGraphics] = None
    subjects: List[SubjectGraphics] = None
    userId: str = None
    tenantId: str = None
