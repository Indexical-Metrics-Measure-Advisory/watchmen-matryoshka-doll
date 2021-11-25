from datetime import datetime
from typing import Any, List

from model.model.common.user import User
from pydantic import BaseModel


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
    unitId: str = None
    conditionResult: bool = None
    name: str = None
    actions: List[UnitActionStatus] = []


class StageRunStatus(ConditionHolder):
    stageId: str = None
    name: str = None
    conditionResult: bool = None
    units: List[UnitRunStatus] = []


class PipelineRunStatus(ConditionHolder):
    status: str = None  # DONE ,ERROR
    pipelineId: str = None
    pipelineName: str = None
    uid: str = None
    startTime: datetime = None
    completeTime: int = None
    pipelineTopicName: str = None
    topicId: str = None
    stages: List[StageRunStatus] = []
    error: str = None
    oldValue: Any = None
    newValue: Any = None
    tenantId: str = None
    currentUser: User = None
    traceId: str = None
