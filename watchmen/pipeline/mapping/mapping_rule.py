from pydantic import BaseModel

from watchmen.raw_data_back.model_field import ModelField
from watchmen.space.factor.factor import Factor


class MappingRule(BaseModel):
    mappingId: str = None
    masterFactor: Factor = None
    lateField:ModelField = None
    hasCodeMapping: bool = False
    codeRule: dict = None
    isBucket: bool = False
    bucketRule: dict = None
    extractRule: str = None
