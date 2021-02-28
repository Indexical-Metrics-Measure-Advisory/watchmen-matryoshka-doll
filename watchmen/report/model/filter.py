from enum import Enum
from typing import List

from pydantic import BaseModel

from watchmen.common.parameter import Parameter


class Filter(BaseModel):
    jointType: str = None
    filters: List['Filter'] = None
    left: Parameter = None
    right: Parameter = None
    operator: str = None


Filter.update_forward_refs()


class ConnectiveType(str, Enum):
    and_type: str = 'and'
    or_type: str = 'or'
