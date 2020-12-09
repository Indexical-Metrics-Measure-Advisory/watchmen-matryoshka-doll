from pydantic import BaseModel

from watchmen.row_data.model_field import ModelField
from watchmen.space.factors.factor import Factor



class MappingRule(BaseModel):
    mappingId: str = None
    masterFactor: Factor = None
    lateField:ModelField = None
    hasCodeMapping: bool = False
    codeRule: dict = None
    isBucket: bool = False
    bucketRule: dict = None
    extractRule: str = None
