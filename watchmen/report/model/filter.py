import operator
from enum import Enum
from pydantic import BaseModel


class Filter(BaseModel):
    topicId: str = None
    factorId: str = None
    operator: str = None
    secondaryTopicId: str = None
    secondaryFactorId: str = None
    value: str = None


class ConnectiveType(str, Enum):
    and_type: str = 'and'
    or_type: str = 'or'



