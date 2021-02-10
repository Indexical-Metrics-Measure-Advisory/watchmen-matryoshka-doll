# from bson import timestamp
from datetime import datetime
from typing import List

from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel


class UnitStatus(MongoModel):
    type: str = None
    complete_time: int = None
    status: str = None
    error: str = None
    uid: str = None


class StageStatus(MongoModel):
    name: str = None
    complete_time: datetime = None
    units: List[UnitStatus] = []


class PipelineRunStatus(MongoModel):
    status: str = None
    pipelineId: str = None
    uid: str = None
    topicId: str = None
    complete_time: int = None
    # stages: List[StageStatus] = []
    error: str = None
