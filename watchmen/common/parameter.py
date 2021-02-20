from typing import List

from pydantic import BaseModel


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


class ParameterJoint(ParameterExpression):
    jointType: str = None
    filters: List[ParameterExpression] = []