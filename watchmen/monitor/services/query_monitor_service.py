import asyncio
import time
from datetime import datetime

from model.model.console_space.console_space import ConsoleSpaceSubject
from model.model.report.report import Report

from watchmen.collection.model.topic_event import TopicEvent
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.monitor.model.query_monitor import QuerySource, QueryMonitor, QuerySummary, ResultSummary
from watchmen.raw_data.service.import_raw_data import import_raw_topic_data


def __build_query_for_subject(condition):
    return condition


def build_query_monitor(subject: ConsoleSpaceSubject, query_type: str):
    query_monitor = QueryMonitor()
    query_monitor.queryUid = get_surrogate_key()
    query_source = QuerySource()
    query_source.name = subject.name
    query_source.queryType = query_type
    query_monitor.querySource = query_source
    return query_monitor


def build_query_monitor_report(report: Report, query_type: str):
    query_monitor = QueryMonitor()
    query_monitor.queryUid = get_surrogate_key()
    query_source = QuerySource()
    query_source.name = report.name
    query_source.queryType = query_type
    query_monitor.querySource = query_source
    return query_monitor


def build_query_summary(sql):
    query_summary = QuerySummary(querySql=sql)
    query_summary.queryTimestamp = datetime.now().replace(tzinfo=None)
    return query_summary


def build_result_summary(row, start):
    result_summary = ResultSummary()
    elapsed_time = time.time() - start
    result_summary.resultCount = len(row)
    result_summary.executionTime = elapsed_time
    return result_summary


async def sync_query_monitor_data(query_monitor: QueryMonitor):
    topic_event = TopicEvent(code="raw_query_monitor", data=query_monitor.dict())

    asyncio.ensure_future(import_raw_topic_data(topic_event))
