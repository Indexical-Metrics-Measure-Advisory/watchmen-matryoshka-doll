from pydantic import BaseModel


class ModelSchemaSet(BaseModel):
    schemas :list=[]
    relationships:list=[]
