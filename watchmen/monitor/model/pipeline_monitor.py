# from bson import timestamp
from typing import Any, List

from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel


class BaseAction(BaseModel):
    type: str = None


class ReadFactorAction(BaseAction):
    type: str = "ReadFactor"
    value: Any = None
    fromTopic: str = None
    fromTopicId: str = None
    fromFactor: str = None
    fromFactorId: str = None


class WriteFactorAction(BaseAction):
    type: str = "WriteFactor"
    value: Any = None
    fromType: str = None
    fromSource: str = None
    fromFactor: str = None
    writeFunction: str = None
    targetTopic: str = None
    targetFactor: str = None


class InsertAndMergeRowAction(BaseAction):
    mapping: list = []
    whereConditions: list = []


class UnitStatus(MongoModel):
    type: str = None
    complete_time: int = None
    status: str = None
    error: str = None
    uid: str = None
    actions: List[BaseAction] = []
    conditions :list = []
    insertCount: int = 0
    updateCount: int = 0
    stageName: str = None


class PipelineRunStatus(MongoModel):
    status: str = None
    pipelineId: str = None
    uid: str = None
    topicId: str = None
    complete_time: int = None
    # stages: List[StageStatus] = []
    error: str = None
    rawId: str = None
