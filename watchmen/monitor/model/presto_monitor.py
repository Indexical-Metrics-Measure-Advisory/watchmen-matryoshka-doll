from pydantic import BaseModel


class PrestoSQLStatus(BaseModel):
    query: str = None
    state: str = None
    executionTime: str = None
    rawInputPositions: str = None
