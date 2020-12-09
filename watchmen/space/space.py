
from typing import List

from pydantic import BaseModel


class Space(BaseModel):
    # id: int = Field( alias='_id')
    topic_list: List = None
    accessUsers: List[str] = None
    name: str = None
    createUser: str = None
    report_list: List = None
    status: bool = True
