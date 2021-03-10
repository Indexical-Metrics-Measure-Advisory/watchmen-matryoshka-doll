import logging

from pypika import functions as fn

from watchmen.common.pagination import Pagination
from watchmen.common.presto.presto_client import get_connection
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_id, \
    load_console_subject_by_report_id
from watchmen.report.engine.sql_builder import _from, _select, _join, _filter, _groupby, _indicator, _orderby, \
    _dimension
from watchmen.report.model.report import ChartType
from watchmen.report.storage.report_storage import load_report_by_id

log = logging.getLogger("app." + __name__)


def build_pagination(pagination):
    offset_num = pagination.pageSize * (pagination.pageNumber - 1)
    return "OFFSET {0} LIMIT {1}".format(offset_num, pagination.pageSize)


def load_dataset_by_subject_id(subject_id, pagination: Pagination):
    ##TODO report monitor
    console_subject = load_console_subject_by_id(subject_id)
    query = build_query_for_subject(console_subject)
    count_query = build_count_query_for_subject(console_subject)
    conn = get_connection()
    cur = conn.cursor()
    count_sql = count_query.get_sql()
    log.info("sql count:{0}".format(count_sql))
    cur.execute(count_sql)
    count_rows = cur.fetchone()
    log.info("sql result: {0}".format(count_rows))

    query_sql = query.get_sql() + " " + build_pagination(pagination)
    log.info("sql:{0}".format(query_sql))
    cur = conn.cursor()
    cur.execute(query_sql)
    rows = cur.fetchall()
    log.debug("sql result: {0}".format(rows))
    return rows, count_rows[0]


def load_chart_dataset(report_id):
    query = build_query_for_subject_chart(report_id)
    conn = get_connection()
    query_sql = query.get_sql()
    log.info("sql: {0}".format(query_sql))
    cur = conn.cursor()
    cur.execute(query_sql)
    rows = cur.fetchall()
    log.debug("sql result: {0}".format(rows))
    return rows


def load_chart_dataset_temp(report):
    query = build_query_for_subject_chart(report.reportId, report)
    conn = get_connection()
    query_sql = query.get_sql()
    log.info("sql: {0}".format(query_sql))
    cur = conn.cursor()
    cur.execute(query_sql)
    rows = cur.fetchall()
    log.debug("sql result: {0}".format(rows))
    return rows


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
    # indicator = report.indicators[0]
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


def build_query_for_subject_chart(chart_id, report=None):
    console_subject = load_console_subject_by_report_id(chart_id)
    columns_dict = column_list_convert_dict(console_subject.dataset.columns)
    if report is None:
        report = load_report_by_id(chart_id)
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
        for dimension in report.dimensions:
            q = _dimension(q, dimension, columns_dict.get(dimension.columnId))
            q = _groupby(q, columns_dict.get(dimension.columnId))
            q = _orderby(q, columns_dict.get(dimension.columnId))
    return q


def column_list_convert_dict(columns) -> dict:
    columns_dict = {}
    for column in columns:
        columns_dict[column.columnId] = column
    return columns_dict
