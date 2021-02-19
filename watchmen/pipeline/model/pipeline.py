from typing import List

from pydantic import BaseModel

from watchmen.common.mongo_model import MongoModel


class Parameter(BaseModel):
    kind: str = None
    type: str = None
    parameters: list = []
    value: str = None
    topicId: str = None
    factorId: str = None


class ParameterExpression(BaseModel):
    left: Parameter = None
    operator: str = None
    right: Parameter = None


class MappingFactor(BaseModel):
    arithmetic: str = None
    source: Parameter = None
    factorId: str = None


class ParameterJoint(ParameterExpression):
    jointType: str = None
    filters: List[ParameterExpression] = []


class Conditional(MongoModel):
    conditional: bool = None
    on: ParameterJoint = None


class UnitAction(Conditional):
    # unitId: str = None
    type: str = None
    targetName: str = None

    # UnitActionAlarm
    severity: str = None
    message: str = None

    # topic
    topicId: str = None
    factorId: str = None
    mapping: List[MappingFactor] = []
    by: ParameterJoint = None
    value: str = None


class ProcessUnit(Conditional):
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
