

from watchmen.common.mongo_model import MongoModel


class UserGroup(MongoModel):
    userGroupId: int=None
    name: str = None
    description: str = None
    userIds: list
    spaceIds: list
