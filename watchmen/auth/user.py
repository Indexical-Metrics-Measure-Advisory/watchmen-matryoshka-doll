from pydantic import BaseModel


class User(BaseModel):
    id:int =None
    username: str= None
    password: str = None
    is_active: bool = True
