# from bson import timestamp
from datetime import datetime
from typing import Any, List

from pydantic import BaseModel

from watchmen.common.model.user import User


class UnitActionStatus(BaseModel):
    type: str = None
    complete_time: int = None
    status: str = None  # DONE ,ERROR
    error: str = None
    uid: str = None
    insertCount: int = 0
    updateCount: int = 0


class MappingHolder(BaseModel):
    mapping: Any = None


class ConditionHolder(BaseModel):
    conditionResult: bool = None


class ReadFactorAction(UnitActionStatus):
    type: str = "ReadFactor"
    value: Any = None


class CopyToMemoryAction(UnitActionStatus):
    type: str = "CopyToMemory"
    value: Any = None


class WriteFactorAction(UnitActionStatus):
    type: str = "WriteFactor"
    value: Any = None
    writeFunction: str = None


class InsertAction(UnitActionStatus, MappingHolder):
    type: str = "InsertRow"


class WhereCondition(BaseModel):
    factor: str = None
    operator: str = None
    value: Any = None


class InsertAndMergeRowAction(UnitActionStatus, MappingHolder):
    type: str = "InsertAndMergeRow"
    whereConditions: List[WhereCondition] = []


class MergeRowAction(UnitActionStatus, MappingHolder):
    type: str = "MergeRow"
    whereConditions: List[WhereCondition] = []


class UnitRunStatus(ConditionHolder):
    actions: List[UnitActionStatus] = []


class StageRunStatus(ConditionHolder):
    name: str = None
    units: List[UnitRunStatus] = []


class PipelineRunStatus(ConditionHolder):
    status: str = None  # DONE ,ERROR
    pipelineId: str = None
    uid: str = None
    startTime: datetime = None
    completeTime: int = None
    topicId: str = None
    stages: List[StageRunStatus] = []
    error: str = None
    oldValue: Any = None
    newValue: Any = None
    tenantId: str = None
    currentUser: User = None
    traceId:int = None
