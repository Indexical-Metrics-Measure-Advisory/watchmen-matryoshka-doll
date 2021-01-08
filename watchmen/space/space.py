from typing import List

from bson import ObjectId
from pydantic import BaseModel, BaseConfig

from watchmen.common.mongo_model import MongoModel


class Space(MongoModel):

    # id: int = Field( alias='_id')
    spaceId: str=None
    topicIds: List = None
    groupIds:List=None
    name: str = None
    description: str = None
    # report_list: List = None
    # status: bool = True
    # accessUsers: List[str] = None



