from typing import List

from watchmen.common.watchmen_model import WatchmenModel


class TopicRelationship(WatchmenModel):
    relationId: str = None
    sourceTopicId: str = None
    sourceFactorNames: List[str] = []
    targetTopicId: str = None
    targetFactorNames: List[str] = [];
    type: str = None
    strictToTarget: bool = False
    strictToSource: bool = False
