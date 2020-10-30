from typing import List

from pydantic import BaseModel, Field


class Topic(BaseModel):
    id: str = Field( alias='_id')
    businessKey  : str = None
    alias: List[str] = None
    indexKey : List[str] = None
    isUnification:bool = False
    embeddedRelationship: List[str] = None
    parentTopicId: str = None





