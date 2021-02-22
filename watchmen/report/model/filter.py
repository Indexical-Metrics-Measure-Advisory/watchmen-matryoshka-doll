from enum import Enum

from pydantic import BaseModel

from watchmen.common.parameter import Parameter


class Filter(BaseModel):
    jointType: str = None
    filters: list = None
    left: Parameter = None
    right: Parameter = None
    operator: str = None


class ConnectiveType(str, Enum):
    and_type: str = 'and'
    or_type: str = 'or'
