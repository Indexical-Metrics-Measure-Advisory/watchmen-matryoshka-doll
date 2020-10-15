


## report definition includes layerout info , factor info , daigram type, filter info, report components info
from pydantic import BaseModel


class Report(BaseModel):
    name:str = None
    question:str = None
    alias: List[str] = None
    filters: List[str]=None
    layouts: List[str]=None

