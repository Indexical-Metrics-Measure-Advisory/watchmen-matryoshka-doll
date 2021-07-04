import logging
import time
import traceback

from pypika import functions as fn

from watchmen.common.pagination import Pagination
from watchmen.common.presto.presto_client import get_connection
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_id, \
    load_console_subject_by_report_id
from watchmen.monitor.model.query_monitor import QueryMonitor
from watchmen.monitor.services.query_monitor_service import build_query_summary, \
    build_result_summary, build_query_monitor
from watchmen.report.engine.sql_builder import _from, _select, _join, _filter, _groupby, _indicator, _orderby, \
    _dimension, _limit
from watchmen.report.model.report import ChartType
from watchmen.report.storage.report_storage import load_report_by_id

log = logging.getLogger("app." + __name__)


def build_pagination(pagination):
    offset_num = pagination.pageSize * (pagination.pageNumber - 1)
    return "OFFSET {0} LIMIT {1}".format(offset_num, pagination.pageSize)


def __find_factor_index(field_list, factor_name):
    for i in range(len(field_list)):
        field = field_list[i]
        if field[0] == factor_name:
            return i
    return None


def get_factor_value_by_subject_and_condition(console_subject, factor_name, filter_list):
    query = build_query_for_subject(console_subject)
    if filter_list:
        query = _filter(query, filter_list)
    conn = get_connection()
    cur = conn.cursor()
    sql = query.get_sql()

    cur.execute(sql)
    rows = cur.fetchall()

    index = __find_factor_index(cur.description, factor_name)

    if index is not None:
        results = []
        for rw in rows:
            results.append(rw[index])
        return results
    else:
        raise KeyError("factor_name :{0} can't find in subject {1}".format(factor_name, console_subject.name))


async def load_dataset_by_subject_id(subject_id, pagination: Pagination,current_user):
    console_subject = load_console_subject_by_id(subject_id,current_user)
    query_monitor: QueryMonitor = build_query_monitor(console_subject, query_type="dataset")
    try:
        # build query condition
        start = time.time()

        query = build_query_for_subject(console_subject)
        count_query = build_count_query_for_subject(console_subject)
        count_sql = count_query.get_sql()

        query_count_summary = build_query_summary(count_sql)
        conn = get_connection()
        cur = conn.cursor()
        log.info("sql count:{0}".format(count_sql))
        cur.execute(count_sql)
        count_rows = cur.fetchone()
        log.info("sql result: {0}".format(count_rows))
        query_count_summary.resultSummary = build_result_summary(count_rows, start)
        query_monitor.querySummaryList.append(query_count_summary)
        query_start = time.time()
        query_sql = query.get_sql() + " " + build_pagination(pagination)
        query_summary = build_query_summary(query_sql)
        log.info("sql:{0}".format(query_sql))
        cur = conn.cursor()
        cur.execute(query_sql)
        rows = cur.fetchall()
        log.debug("sql result: {0}".format(rows))
        query_summary.resultSummary = build_result_summary(rows, query_start)
        query_monitor.querySummaryList.append(query_summary)
        query_monitor.executionTime = time.time() - start
        return rows, count_rows[0]
    except Exception as e:
        log.exception(e)
        query_monitor.error = traceback.format_exc()
        query_monitor.success = False
    finally:
        await save_query_monitor_data(query_monitor)
        # return [],0


async def save_query_monitor_data(query_monitor):
    pass  ## TODO save_query_monitor_data
    # await sync_query_monitor_data(query_monitor)


async def load_chart_dataset(report_id,current_user):
    # assert report_id is None
    report = load_report_by_id(report_id,current_user)

    print("report", report)
    # query_monitor = build_query_monitor_report(report, query_type="report")
    try:
        query = build_query_for_subject_chart(report_id, report)
        # query_count_summary = build_query_summary(count_sql)
        rows = __load_chart_dataset(query, query_monitor=None)
        return rows
    except Exception as e:
        log.exception(e)
        # query_monitor.error = traceback.format_exc()
        # query_monitor.success = False
    # finally:
    #     await save_query_monitor_data(query_monitor)


def __load_chart_dataset(query, query_monitor=None):
    start = time.time()
    conn = get_connection()
    query_sql = query.get_sql()
    query_sql_summary = build_query_summary(query_sql)
    log.info("sql: {0}".format(query_sql))
    cur = conn.cursor()
    cur.execute(query_sql)
    rows = cur.fetchall()
    log.debug("sql result: {0}".format(rows))
    query_sql_summary.resultSummary = build_result_summary(rows, start)

    if query_monitor:
        query_monitor.querySummaryList.append(query_sql_summary)
        query_monitor.executionTime = time.time() - start
    return rows or []


def load_chart_dataset_temp(report,current_user):
    query = build_query_for_subject_chart(report.reportId, report,current_user)
    return __load_chart_dataset(query)


def build_query_for_subject(console_subject):
    dataset = console_subject.dataset
    query = None
    if dataset is not None:
        query = _from(dataset.columns[0])
        for column in dataset.columns:
            query = _select(query, column)
        for join in dataset.joins:
            query = _join(query, join)
        if dataset.filters:
            query = _filter(query, dataset.filters)
    return query


def build_count_query_for_subject_chart(console_subject, columns_dict, report):
    dataset = console_subject.dataset
    query = None
    if dataset is not None:
        query = _from(dataset.columns[0])
        if report.indicators:
            for indicator in report.indicators:
                query = _indicator(query, indicator, columns_dict.get(indicator.columnId))
        else:
            query = query.select(fn.Count("*"))
        for join in dataset.joins:
            query = _join(query, join)
        if dataset.filters:
            query = _filter(query, dataset.filters)
    return query


def build_count_query_for_subject(console_subject):
    dataset = console_subject.dataset
    query = None
    # indicator = report.indicators[0]
    if dataset is not None:
        query = _from(dataset.columns[0])
        query = query.select(fn.Count("*"))
        for join in dataset.joins:
            query = _join(query, join)
        if dataset.filters:
            query = _filter(query, dataset.filters)
    return query


def build_query_for_subject_chart(chart_id, report=None,current_user=None):
    console_subject = load_console_subject_by_report_id(chart_id,current_user)
    columns_dict = column_list_convert_dict(console_subject.dataset.columns)
    if report is None:
        report = load_report_by_id(chart_id,current_user)
    if report.chart.type == ChartType.COUNT:
        q = build_count_query_for_subject_chart(console_subject, columns_dict, report)
    else:
        dataset = console_subject.dataset
        q = _from(dataset.columns[0])
        for join in dataset.joins:
            q = _join(q, join)
        if dataset.filters:
            q = _filter(q, dataset.filters)
        for indicator in report.indicators:
            q = _indicator(q, indicator, columns_dict.get(indicator.columnId))

        truncation = report.chart.settings.get('truncation', None)
        if truncation is not None:
            truncation_type = truncation['type']
            count = truncation['count']

        for dimension in report.dimensions:
            q = _dimension(q, dimension, columns_dict.get(dimension.columnId))
            q = _groupby(q, columns_dict.get(dimension.columnId))
            if truncation is not None:
                if truncation_type == "top":
                    q = _orderby(q, columns_dict.get(dimension.columnId), "asc")
                if truncation_type == "bottom":
                    q = _orderby(q, columns_dict.get(dimension.columnId), "desc")
                if truncation_type == "none":
                    q = _orderby(q, columns_dict.get(dimension.columnId), "none")
            else:
                q = _orderby(q, columns_dict.get(dimension.columnId), "none")

        if truncation is not None:
            q = _limit(q, count)
    return q


def column_list_convert_dict(columns) -> dict:
    columns_dict = {}
    for column in columns:
        columns_dict[column.columnId] = column
    return columns_dict
