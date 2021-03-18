from typing import List

from watchmen.common.mongo_model import MongoModel


class Space(MongoModel):
    spaceId: str = None
    topicIds: List = None
    groupIds: List = None
    name: str = None
    description: str = None
