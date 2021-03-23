# from bson import timestamp
from typing import Any, List

from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel


class BaseAction(BaseModel):
    type: str = None


class UnitActionStatus(BaseAction):
    type: str = None
    complete_time: int = None
    status: str = None
    error: str = None
    uid: str = None
    conditions: list = []
    insertCount: int = 0
    updateCount: int = 0


class FromTopicHolder(BaseModel):
    fromTopic: str = None
    fromTopicId: str = None
    fromFactor: str = None
    fromFactorId: str = None


class TargetTopicHolder(BaseModel):
    targetTopic: str = None
    targetTopicId: str = None
    targetFactor: str = None
    targetFactorId: str = None


class MappingHolder(BaseModel):
    mapping: list = []


class ConditionHolder(BaseModel):
    conditions: list = []


class ReadFactorAction(UnitActionStatus, FromTopicHolder):
    type: str = "ReadFactor"
    value: Any = None


class WriteFactorAction(UnitActionStatus, FromTopicHolder, TargetTopicHolder):
    type: str = "WriteFactor"
    value: Any = None
    writeFunction: str = None


class InsertAction(UnitActionStatus, MappingHolder):
    type: str = "InsertRow"


class InsertAndMergeRowAction(UnitActionStatus, FromTopicHolder, MappingHolder):
    type: str = "InsertAndMergeRow"
    whereConditions: list = []


class UnitRunStatus(ConditionHolder):
    actions: List[UnitActionStatus] = []


class StageRunStatus(ConditionHolder):
    name: str = None
    units: List[UnitRunStatus] = []


class PipelineRunStatus(MongoModel, ConditionHolder):
    status: str = None
    pipelineId: str = None
    pipelineName: str = None
    uid: str = None
    topicId: str = None
    complete_time: int = None
    stages: List[StageRunStatus] = []
    error: str = None
    pipelineType: str = None
    oldValue: Any = None
    newValue: Any = None
