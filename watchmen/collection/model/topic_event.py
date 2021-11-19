from typing import Any

from pydantic import BaseModel


class TopicEvent(BaseModel):
    type: str = None
    code: str = None
    data: Any = None
    previous_data: Any = None
    trigger_type: str = None
    pat: str = None
    user: str = None
