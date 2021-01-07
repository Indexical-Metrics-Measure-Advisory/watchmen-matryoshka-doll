from typing import List

from pydantic import BaseModel


class Space(BaseModel):
    # id: int = Field( alias='_id')
    spaceId: int
    topicIds: List = None

    name: str = None
    description: str = None
    # report_list: List = None
    # status: bool = True
    # accessUsers: List[str] = None
