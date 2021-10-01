from typing import List

from pydantic import BaseModel

from watchmen.common.parameter import Parameter, ParameterJoint
from watchmen.common.watchmen_model import WatchmenModel


class MappingFactor(BaseModel):
    arithmetic: str = None
    source: Parameter = None
    factorId: str = None


class Conditional(WatchmenModel):
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
    source: Parameter = None
    externalWriterId: str = None
    eventCode: str = None


class ProcessUnit(Conditional):
    unitId: str = None
    name: str = None
    loopVariableName: str = None
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
    tenantId: str = None
