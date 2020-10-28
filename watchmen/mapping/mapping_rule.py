from pydantic import BaseModel

from watchmen.factors.model.factor import Factor


class MappingRule(BaseModel):
    mappingId: str = None
    masterFactor: Factor = None
    hasCodeMapping: bool = False
    codeRule: dict = None
    isBucket: bool = False
    bucketRule: dict = None
    extractRule: str = None
