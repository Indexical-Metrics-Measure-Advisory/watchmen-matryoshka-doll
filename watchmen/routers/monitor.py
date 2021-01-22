from typing import List

from fastapi import APIRouter

from watchmen.monitor.model.presto_monitor import PrestoSQLStatus
from watchmen.monitor.presto.index import load_query_status_from_presto

router = APIRouter()




