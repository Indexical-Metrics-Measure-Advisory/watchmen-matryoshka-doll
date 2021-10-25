from enum import Enum


class ValueKind(Enum):
    table = "TABLE"
    field = "FIELD"
    function = "FUNCTION"
    arithmetic = "ARITHMETIC"
    constant = "CONSTANT"
