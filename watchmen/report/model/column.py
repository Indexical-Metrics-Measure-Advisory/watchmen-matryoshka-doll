from enum import Enum

from pydantic import BaseModel

from watchmen.common.parameter import Parameter


class Column(BaseModel):
    columnId: str = None
    parameter: Parameter = None
    alias: str = None


class Operator(str, Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"
    modulus = "modulus"
