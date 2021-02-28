from typing import List

from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel
from watchmen.common.parameter import Parameter, ParameterJoint


class MappingFactor(BaseModel):
    arithmetic: str = None
    source: Parameter = None
    factorId: str = None


class Conditional(MongoModel):
    conditional: bool = None
    on: ParameterJoint = None


class UnitAction(Conditional):
    # unitId: str = None
    actionId: str = None
    type: str = None
    variableName: str = None

    # UnitActionAlarm
    severity: str = None
    message: str = None
    arithmetic: str = None

    # topic
    topicId: str = None
    factorId: str = None
    mapping: List[MappingFactor] = []
    by: ParameterJoint = None
    # value: str = None
    source: Parameter = None


class ProcessUnit(Conditional):
    unitId: str = None
    # on: CompositeCondition = None;
    do: List[UnitAction] = []


class Stage(Conditional):
    stageId: str = None;
    name: str = None
    units: List[ProcessUnit] = []


class Pipeline(Conditional):
    pipelineId: str = None
    topicId: str = None
    name: str = None
    type: str = None
    stages: List[Stage] = []
    enabled: bool = None
