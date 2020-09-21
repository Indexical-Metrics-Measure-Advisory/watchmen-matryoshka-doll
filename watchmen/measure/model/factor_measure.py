from pydantic import BaseModel


class FactorMeasure(BaseModel):
    measureId: str = None
    type: str = None
