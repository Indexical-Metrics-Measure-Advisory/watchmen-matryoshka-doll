from typing import Any, List

from pydantic import BaseModel


class WhereCondition(BaseModel):
    factor: str = None
    operator: str = None
    value: Any = None


# class PreCondition(BaseModel):


class ActionStatus(BaseModel):
    type: str = None
    completeTime: int = None
    status: str = None  # DONE ,ERROR
    error: str = None
    uid: str = None
    insertCount: int = 0
    updateCount: int = 0
    whereConditions: List[WhereCondition] = []
    mapping: Any = None
    value: Any = None
    by: Any = None
