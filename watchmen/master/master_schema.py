


## topic list

## name

## version info

##
from typing import List

from pydantic import BaseModel

from watchmen.factors.model.topic import Topic


class MasterSchema(BaseModel):
     id : str = None
     topic_list:List[Topic] = None
     user: str = None
