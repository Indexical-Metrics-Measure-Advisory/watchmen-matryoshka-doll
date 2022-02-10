from __future__ import annotations

from typing import List

from pydantic import BaseModel


class ParameterJoint(BaseModel):
    jointType: str = None
    filters: List[ParameterJoint] = []
    left: Parameter = None
    operator: str = None
    right: Parameter = None


class Parameter(BaseModel):
    kind: str = None
    type: str = None
    parameters: List[Parameter] = []
    conditional: bool = False
    on: ParameterJoint = None
    value: str = None
    topicId: str = None
    factorId: str = None


# for self-referencing model, need python 3.7+
ParameterJoint.update_forward_refs()
Parameter.update_forward_refs()
