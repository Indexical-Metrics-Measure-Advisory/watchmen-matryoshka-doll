import logging
import time

from model.model.report.report import Report
from pypika import AliasedQuery
from pypika import Order

from watchmen.common.presto.presto_client import get_connection
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_report_id
from watchmen.monitor.services.query_monitor_service import build_query_summary, build_result_summary
from watchmen.report.builder.dialects import PrestoQuery
from watchmen.report.builder.funnel import build_report_funnels
from watchmen.report.builder.report_filer import build_indicators, build_dimensions, build_report_where
from watchmen.report.builder.space_filter import get_topic_sub_query_with_space_filter
from watchmen.report.engine.dataset_engine import build_dataset_query_for_subject
from watchmen.report.storage.report_storage import load_report_by_id

log = logging.getLogger("app." + __name__)


def build_query_for_chart(chart_id, current_user):
    console_subject = load_console_subject_by_report_id(chart_id, current_user)
    report: Report = load_report_by_id(chart_id, current_user)
    # print(report.dimensions)
    return __build_chart_query(report, console_subject, current_user)


def __build_chart_query(report, console_subject, current_user):
    q = build_dataset_query_for_subject(console_subject, current_user)
    dataset_query_alias = "chart_dataset"
    chart_query = PrestoQuery.with_(q, dataset_query_alias).from_(AliasedQuery(dataset_query_alias))
    _indicator_selects, _indicator_in_group_by = build_indicators(report.indicators,
                                                                  console_subject.dataset.columns,
                                                                  dataset_query_alias)
    chart_query = chart_query.select(*_indicator_selects).groupby(*_indicator_in_group_by)
    _selects, _groupbys, _orderbys = build_dimensions(report.dimensions,
                                                      console_subject.dataset.columns,
                                                      dataset_query_alias)
    chart_query = chart_query.select(*_selects).groupby(*_groupbys)
    if report.chart.settings:
        truncation = report.chart.settings.get('truncation', None)
        if truncation:
            truncation_type = truncation.get('type')
            count = truncation.get('count', None)
            if truncation_type == "top":
                chart_query = chart_query.orderby(*_orderbys, order=Order.asc)
            elif truncation_type == "bottom":
                chart_query = chart_query.orderby(*_orderbys, order=Order.desc)
            else:
                chart_query = chart_query.orderby(*_orderbys)
            if count:
                chart_query = chart_query.limit(count)

    if report.filters:
        topic_space_filter = get_topic_sub_query_with_space_filter(console_subject, current_user)
        chart_query = chart_query.where(build_report_where(report.filters,
                                                           topic_space_filter,
                                                           dataset_query_alias,
                                                           console_subject.dataset.columns
                                                           ))
    if report.funnels:
        chart_query = chart_query.where(build_report_funnels(report.funnels,
                                                             dataset_query_alias,
                                                             console_subject.dataset.columns
                                                             ))
    return chart_query


async def load_chart_dataset(report_id, current_user):
    try:
        query = build_query_for_chart(report_id, current_user)

        if query is None or query.get_sql() == "":
            return []
        else:
            rows = __load_chart_dataset(query, query_monitor=None)
            return rows
    except Exception as e:
        log.exception(e)


def __load_chart_dataset(query, query_monitor=None):
    start = time.time()
    conn = get_connection()
    query_sql = query.get_sql()
    query_sql_summary = build_query_summary(query_sql)
    log.info("sql: {0}".format(query_sql))
    # print(query_sql)
    cur = conn.cursor()
    cur.execute(query_sql)
    rows = cur.fetchall()
    log.debug("sql result: {0}".format(rows))
    query_sql_summary.resultSummary = build_result_summary(rows, start)

    if query_monitor:
        query_monitor.querySummaryList.append(query_sql_summary)
        query_monitor.executionTime = time.time() - start
    return rows or []


def load_chart_dataset_temp(report, current_user):
    console_subject = load_console_subject_by_report_id(report.reportId, current_user)
    query = __build_chart_query(report, console_subject, current_user)
    if query is None or query.get_sql() == "":
        return []
    else:
        return __load_chart_dataset(query)
