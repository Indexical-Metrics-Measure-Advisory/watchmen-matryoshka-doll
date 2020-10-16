from typing import List

from pydantic import BaseModel


class Topic(BaseModel):
    topicId: str = None
    businessKey  : str = None
    alias: List[str] = None
    indexKey : List[str] = None
    isUnification:bool = False
    embeddedRelationship: List[str] = None
    parentTopicId: str = None





