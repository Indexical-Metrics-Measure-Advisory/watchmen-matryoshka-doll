from typing import List

from pydantic.main import BaseModel


class ConditionResult(BaseModel):
    logicOperator: str = None
    resultList: List = []
