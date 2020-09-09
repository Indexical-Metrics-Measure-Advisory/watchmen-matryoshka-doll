from typing import List

from pydantic import BaseModel


class Topic(BaseModel):
    topicId: str = None
    name: str = None
    tags: List[str] =[]



