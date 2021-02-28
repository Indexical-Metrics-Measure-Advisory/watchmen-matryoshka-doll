from enum import Enum
from typing import List

from pydantic import BaseModel


class ParameterKind(Enum):
    TOPIC = 'topic',
    CONSTANT = 'constant',
    COMPUTED = 'computed'


class Parameter(BaseModel):
    kind: str = None
    type: str = None
    parameters: List['Parameter'] = []
    value: str = None
    topicId: str = None
    factorId: str = None


# for self-referencing model, need python 3.7+
Parameter.update_forward_refs()


class ParameterExpression(BaseModel):
    left: Parameter = None
    operator: str = None
    right: Parameter = None


class ParameterJoint(ParameterExpression):
    jointType: str = None
    filters: List[ParameterExpression] = []
