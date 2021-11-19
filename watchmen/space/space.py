from typing import List

from pydantic import BaseModel

from watchmen.common.parameter import ParameterJoint
from watchmen.common.watchmen_model import WatchmenModel


class SpaceFilter(BaseModel):
    enabled: bool = False
    joint: ParameterJoint = None
    topicId: str = None


class Space(WatchmenModel):
    spaceId: str = None
    topicIds: List[str] = None
    groupIds: List[str] = None
    name: str = None
    description: str = None
    tenantId: str = None
    filters: List[SpaceFilter] = None
