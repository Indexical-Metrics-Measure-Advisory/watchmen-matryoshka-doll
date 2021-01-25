from typing import List

from watchmen.common.mongo_model import MongoModel


class TopicRelationship(MongoModel):
    relationId: str = None
    sourceTopicId: str = None
    sourceFactorNames: List[str] = []
    targetTopicId: str = None
    targetFactorNames: List[str] = [];
    type: str = None
    strictToTarget: bool = False
    strictToSource: bool = False