from watchmen.common.mongo_model import MongoModel


class User(MongoModel):
    userId: str = None
    name: str = None
    nickName: str = None
    password: str = None
    is_active: bool = True
    groupIds: list = None
    role: str = None

    # userId?: string;
    # name?: string;
    # nickName?: string;
