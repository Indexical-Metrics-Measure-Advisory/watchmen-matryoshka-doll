from pydantic import BaseModel


class FactorDimension(BaseModel):
    dimensionId:str = None
    code:str = None


