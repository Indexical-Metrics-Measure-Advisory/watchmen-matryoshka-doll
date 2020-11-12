


## topic list

## name

## version info

##
from typing import List

from pydantic import BaseModel, Field

class MasterSchema(BaseModel):
     # id: int = Field( alias='_id')
     topic_id_list:List = None
     user: str = None
     name:str = None

