from datetime import datetime
from typing import List

from pydantic.main import BaseModel

from watchmen.common.mongo_model import MongoModel


class QuerySource(BaseModel):
    name: str = None
    queryType: str = None
    queryTimestamp: datetime = None


class ResultSummary(BaseModel):
    resultCount: int = None
    executionTime: int = None


class QuerySummary(BaseModel):
    querySql: str = None
    queryTimestamp: datetime = None
    resultSummary: ResultSummary = None


class QueryMonitor(MongoModel):
    queryUid: int = None
    querySource: QuerySource = None
    querySummaryList: List[QuerySummary] = []
    executionTime: int = None
    success: bool = True
    error: str = None
