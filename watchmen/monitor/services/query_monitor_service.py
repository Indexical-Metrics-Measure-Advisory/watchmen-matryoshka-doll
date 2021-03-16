import time
from datetime import datetime

from watchmen.console_space.model.console_space import ConsoleSpaceSubject
from watchmen.monitor.model.query_monitor import QuerySource, QueryMonitor, QuerySummary, ResultSummary


def __build_query_for_subject(condition):
    return condition


def build_query_monitor(subject: ConsoleSpaceSubject, query_type: str):
    query_monitor = QueryMonitor()
    query_source = QuerySource()
    query_source.name = subject.name
    query_source.queryType = query_type
    query_monitor.querySource = query_source
    return query_monitor


def build_query_summary(sql):
    query_summary = QuerySummary(querySql=sql)
    query_summary.queryTimestamp = datetime.now()
    return query_summary


def build_result_summary(row, start):
    result_summary = ResultSummary()
    elapsed_time = time.time() - start
    result_summary.resultCount = len(row)
    result_summary.executionTime = elapsed_time
    return result_summary


def build_monitor_result_summary():
    pass


# def build_query_monitor():
#     pass
