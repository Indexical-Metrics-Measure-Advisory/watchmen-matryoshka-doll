from pydantic import BaseModel

from watchmen.event.event import Event


class DataEntitySet(BaseModel):
    id:str=None
    entities:list=[]
    relationships :list=[]
    # domainId:str=None
    domain:str=None
    subDomainId:str=None
    event:Event=None


class Event(object):
    code: str
    type: str
