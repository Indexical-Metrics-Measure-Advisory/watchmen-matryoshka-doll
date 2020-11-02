


## topic list

## name

## version info

##
from typing import List

from pydantic import BaseModel, Field

from watchmen.factors.model.topic import Topic


class MasterSchema(BaseModel):
     # id: int = Field( alias='_id')
     topic_list:List = None
     user: str = None
     name:str = None
