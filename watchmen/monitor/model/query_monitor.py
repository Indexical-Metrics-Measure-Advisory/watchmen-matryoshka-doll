from datetime import datetime

from pydantic.main import BaseModel

from watchmen.common.mongo_model import MongoModel


class QueryCondition(BaseModel):
    querySql: str = None
    name:str = None
    queryType :str = None
    queryTimestamp : datetime = None


class ResultSummary(BaseModel):
    resultCount: int = None


class QueryMonitor(MongoModel):
    queryCondition: QueryCondition = None
    executionTime: int = None
    resultSummary: ResultSummary = None



