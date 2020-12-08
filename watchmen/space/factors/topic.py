from typing import List

from pydantic import BaseModel
from watchmen.space.factors.factor import Factor


class Topic(BaseModel):

    topicId: str = None

    topic_name: str = None

    businessKey  : str = None

    factors: List[Factor] = []

    alias: List[str] = None

    indexKey : List[str] = None

    isUnification:bool = False

    embeddedRelationship: List[str] = None

    parentTopicId: str = None

