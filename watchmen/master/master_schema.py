


## topic list

## name

## version info

##
from typing import List

from pydantic import BaseModel


class MasterSchema(BaseModel):
     id : str = None
     topic_list:List = None
     user: str = None
