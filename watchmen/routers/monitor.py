from typing import List

from fastapi import APIRouter

from watchmen.monitor.model.presto_monitor import PrestoSQLStatus
from watchmen.monitor.presto.index import load_query_status_from_presto

router = APIRouter()


@router.get("/monitor/sql/status", tags=["monitor"], response_model=List[PrestoSQLStatus])
async def load_query_status():
    result = []
    sql_status_list = load_query_status_from_presto()
    for sql_status in sql_status_list:
        presto_sql_status = PrestoSQLStatus()
        presto_sql_status.query = sql_status["query"]
        presto_sql_status.executionTime = sql_status["queryStats"]["executionTime"]
        presto_sql_status.rawInputPositions = sql_status["queryStats"]["rawInputPositions"]
        presto_sql_status.state = sql_status["state"]
        result.append(presto_sql_status)
    return result

