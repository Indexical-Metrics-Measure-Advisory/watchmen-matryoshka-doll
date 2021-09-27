from typing import Any

from pydantic import BaseModel


class TopicEvent(BaseModel):
    type: str = None
    code: str = None
    data: Any = None

