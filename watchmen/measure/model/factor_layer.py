from pydantic import BaseModel


class FactorLayer(BaseModel):
    layerId:str = None
    code:str = None
    description:str = None
