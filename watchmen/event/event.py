# import datetime

from pydantic import BaseModel


class Event(BaseModel):
    type:str = None
    description:str = None
    # time: datetime = None
