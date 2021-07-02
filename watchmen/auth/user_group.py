from watchmen.common.watchmen_model import WatchmenModel


class UserGroup(WatchmenModel):
    userGroupId: str = None
    name: str = None
    description: str = None
    userIds: list = None
    spaceIds: list = None
    tenantId:str =None
