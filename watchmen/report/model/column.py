from enum import Enum
from pydantic import BaseModel


class Column(BaseModel):
    topicId: str = None
    factorId: str = None
    operator: str = None
    secondaryTopicId: str = None
    secondaryFactorId: str = None
    alias: str = None


class Operator(str, Enum):
    asIs = "asis"
    add = "add"
    subtract = "subtract"
    multiply = "multiply"
    divide = "divide"
    modulus = "modulus"

