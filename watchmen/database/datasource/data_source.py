from typing import List

from pydantic import BaseModel

from watchmen.common.watchmen_model import WatchmenModel


class DataSourceParam(BaseModel):
    name:str = None
    value:str = None


class DataSource(WatchmenModel):
    dataSourceId:str = None
    dataSourceCode:str = None
    dataSourceType:str=None
    host:str = None
    port:str=None
    username:str= None
    password:str= None
    name:str=None
    url:str=None
    params:List[DataSourceParam] = []
    tenantId: str = None
