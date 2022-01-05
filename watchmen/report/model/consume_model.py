from __future__ import annotations
from pydantic.main import BaseModel
from typing import List, Any


class Where(BaseModel):
    jointType: str = None
    filters: List[Where] = []
    name: str = None
    type: str = None
    operator: str = None
    value: Any = None


Where.update_forward_refs()


class Indicator(BaseModel):
    name: str = None
    arithmetic: str = None
    alias: str = None


class Query(BaseModel):
    subject_name: str = None
    indicators: List[Indicator] = []
    where: Where = None
