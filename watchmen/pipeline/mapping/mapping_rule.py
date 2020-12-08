from pydantic import BaseModel

from watchmen.space.factors.factor import Factor
from watchmen.space.row_data import ModelField


class MappingRule(BaseModel):
    mappingId: str = None
    masterFactor: Factor = None
    lateField:ModelField = None
    hasCodeMapping: bool = False
    codeRule: dict = None
    isBucket: bool = False
    bucketRule: dict = None
    extractRule: str = None
