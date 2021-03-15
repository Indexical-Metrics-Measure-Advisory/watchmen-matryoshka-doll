from datetime import datetime

from watchmen.console_space.model.console_space import ConsoleSpaceSubject
from watchmen.monitor.model.query_monitor import QueryCondition


def __build_query_for_subject(condition):
    return condition


def build_query_condition_subject(subject: ConsoleSpaceSubject, query_sql: str, query_type: str):
    query_condition = QueryCondition()
    query_condition.queryType = query_type
    query_condition.queryTimestamp = datetime.now()
    query_condition.name = subject.name
    query_condition.querySql = query_sql
    return query_condition


def build_monitor_result_summary():
    pass


def build_query_monitor():
    pass
