from pydantic import BaseModel


class DataEntitySet(BaseModel):
    id:str=None
    entities:list=[]
    relationships :list=[]
    domainId:str=None
    subDomainId:str=None


