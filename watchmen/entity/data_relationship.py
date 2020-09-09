from pydantic import BaseModel


class DataRelationship(BaseModel):
    code:str=None
    id:str=None
    parent_id:str=None
    child_id:str=None



