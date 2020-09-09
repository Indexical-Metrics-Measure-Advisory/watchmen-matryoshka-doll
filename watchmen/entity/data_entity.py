from watchmen.entity.data_entity_set import DataEntitySet
from pydantic import BaseModel

class DataEntity(BaseModel):

    attr:dict={}
    entity_set:DataEntitySet=None




