from typing import List

from pydantic import BaseModel
from watchmen.factors.model.factor import Factor


class Topic(BaseModel):

    topicId: str = None

    topic_name: str = None

    businessKey  : str = None

    factors: List[Factor] = None

    alias: List[str] = None

    indexKey : List[str] = None

    isUnification:bool = False

    embeddedRelationship: List[str] = None

    parentTopicId: str = None

