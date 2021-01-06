from pydantic import BaseModel


class User(BaseModel):
    userId:int =None
    name: str= None
    nickName: str = None
    password: str = None
    is_active: bool = True
    groupIds:list=None

    # userId?: string;
    # name?: string;
    # nickName?: string;
