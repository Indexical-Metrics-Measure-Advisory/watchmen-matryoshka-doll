from watchmen.common.watchmen_model import WatchmenModel


class User(WatchmenModel):
    userId: str = None
    name: str = None
    nickName: str = None
    password: str = None
    is_active: bool = True
    groupIds: list = None
    role: str = None
    tenantId:str =None
