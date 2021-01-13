from typing import List

from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel


# class SimpleFuncArithmetic(BaseModel):

class SimpleFuncValue(BaseModel):
    arithmetic: str = None
    type: str = None
    name: str = None
    topicId:str = None
    topicId:str = None


class Condition(BaseModel):
    left: SimpleFuncValue=None;
    operator: str=None;
    right: SimpleFuncValue=None;


class CompositeCondition(BaseModel):
    mode: str = None;
    children: List[Condition] = [];


class Trigger(BaseModel):
    type: str = None
    relatedTopicName: str = None




# class MappingFactor(BaseModel):
#
# 	from: SimpleFuncValue
# 	to: SimpleFuncValue


class UnitAction(BaseModel):
    # unitId: str = None
    type: str = None
    targetName: str = None

    # UnitActionAlarm
    severity: str = None
    message: str = None

    # topic
    topicId: str = None
    factorId: str = None
    mapping: list = []
    by: CompositeCondition = None;
    value: str = None


class ProcessUnit(BaseModel):
    on: CompositeCondition = None;
    do: List[UnitAction] = [];


class Stage(BaseModel):
    stageId: str = None;
    name: str = None
    units: List[ProcessUnit] = [];


class Pipeline(MongoModel):
    pipelineId: str = None
    topicId: str = None;
    name: str = None;
    type: str = None;
    stages: List[Stage] = []
