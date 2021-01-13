from typing import List

from watchmen.common.mongo_model import MongoModel
from watchmen.topic.factor.factor import Factor


class Topic(MongoModel):
    topicId: str = None
    name: str = None
    code: str = None
    type: str = None
    factors: List[Factor] = []
    description: str = None
    # alias: List[str] = None
    # is_aggregate: bool = False
    # businessKey: list = []

    '''
    topic_id: str = None

    topic_name: str = None

    businessKey  : str = None

    factors: List[Factor] = []

    alias: List[str] = None

    indexKey : List[str] = None

    isUnification:bool = False

    embeddedRelationship: List[str] = None

    parentTopicId: str = None
    '''
