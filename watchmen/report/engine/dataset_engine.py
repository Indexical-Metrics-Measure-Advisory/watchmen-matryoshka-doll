import logging
import operator

from pypika import Query, Table, JoinType
from pypika import functions as fn

from watchmen.common.pagination import Pagination
from watchmen.common.presto.presto_client import get_connection
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_id, \
    load_console_subject_by_report_id
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.report.engine.sql_builder import _from, _select, _join, _connective_filter, _filter, _groupby, _indicator
from watchmen.report.storage.report_storage import load_report_by_id
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

log = logging.getLogger("app." + __name__)


def build_columns(columns, is_count):
    topic_dict = {}

    table_dict = {}

    topic = get_topic_by_id(columns[0].topicId)
    key = build_collection_name(topic.name)
    for column in columns:
        topic = get_topic_by_id(column.topicId)
        key = build_collection_name(topic.name)
        if key in topic_dict:
            factor = get_factor(column.factorId, topic)
            topic_dict[key].append(factor.name)
        else:
            topic_dict[key] = []
            factor = get_factor(column.factorId, topic)
            topic_dict[key].append(factor.name)

    q = Query._builder()
    q = q.from_(Table(key))
    if is_count:
        q = q.select(fn.Count("*"))
        for key, items in topic_dict.items():
            t = Table(key)
            table_dict[key] = t
    else:
        for key, items in topic_dict.items():
            t = Table(key)
            table_dict[key] = t
            for item in items:
                q = q.select(t[item])
    return q, table_dict


def get_join_type(join_type):
    if join_type == "inner":
        return JoinType.inner
    elif join_type == "left":
        return JoinType.left
    elif join_type == "right":
        return JoinType.right
    else:
        raise Exception("join_type is not supported")


def _add_joins(joins, query):
    for join_table, criterion, join_type in joins:
        query = query.join(join_table, how=join_type).on(criterion)
    return query


def build_joins(joins, query, table_dict):
    joins_data_list = []
    for join in joins:
        topic = get_topic_by_id(join.topicId)
        table = table_dict[build_collection_name(topic.name)]
        factor = get_factor(join.factorId, topic)
        secondary_topic = get_topic_by_id(join.secondaryTopicId)
        secondary_table = table_dict[build_collection_name(secondary_topic.name)]
        secondary_factor = get_factor(join.secondaryFactorId, secondary_topic)
        join_type = get_join_type(join.type)
        joins_data_list.append(
            (table, operator.eq(secondary_table[secondary_factor.name], table[factor.name]), join_type))

    # print(joins_data_list)
    return _add_joins(joins_data_list, query)


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
    # count =cur.
    rows = cur.fetchall()
    log.info("sql result: {0}".format(rows))
    # print("sql count:", count)
    return rows, count_rows[0]

'''
def load_chart_dataset(subject_id, chart_id):
    query = build_query_for_subject_chart(subject_id, chart_id)
    conn = get_connection()
    query_sql = query.get_sql()
    log.info("sql: {0}".format(query_sql))
    cur = conn.cursor()
    cur.execute(query_sql)
    rows = cur.fetchall()

    log.info("sql result: {0}".format(rows))
    return rows
'''

def load_chart_dataset(chart_id):
    query = build_query_for_subject_chart(chart_id)
    conn = get_connection()
    query_sql = query.get_sql()
    log.info("sql: {0}".format(query_sql))
    cur = conn.cursor()
    cur.execute(query_sql)
    rows = cur.fetchall()
    log.info("sql result: {0}".format(rows))
    return rows


def get_sql_operator(opt):
    if opt == "more":
        return operator.ge
    elif opt == "equals":
        return operator.eq
    elif opt == "not-equals":
        return operator.ne
    elif opt == "less":
        return operator.le
    elif opt == "less-equals":
        return operator.lt
    elif opt == "more-equals":
        return operator.gt
    else:
        # TODO more operator support
        raise Exception("operator is not supported")
    # elif operator == "in":
    #     return ""


def build_where(filter_groups, query, table_dict):
    for filter_group in filter_groups:
        if len(filter_group.filters) > 1:
            # TODO  build join group condition

            pass
        else:
            if filter_group.filters:
                filter_data = filter_group.filters[0]
                topic = get_topic_by_id(filter_data.topicId)
                table = table_dict[build_collection_name(topic.name)]
                factor = get_factor(filter_data.factorId, topic)
                opt = get_sql_operator(filter_data.operator)
                condition = opt(table[factor.name], int(filter_data.value))
                query = query.where(condition)
                return query
            else:
                return query


'''
def build_query_for_subject(console_subject):
    dataset = console_subject.dataset
    query = None
    if dataset is not None:
        # build columns
        if dataset.columns:
            query, table_dict = build_columns(dataset.columns, False)
        if dataset.filters:
            query = build_where(dataset.filters, query, table_dict)
        if dataset.joins:
            query = build_joins(dataset.joins, query, table_dict)
    return query
'''


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

'''
def build_count_query_for_subject(console_subject):
    dataset = console_subject.dataset
    # query =None
    if dataset is not None:
        if dataset.columns:
            query, table_dict = build_columns(dataset.columns, True)
        if dataset.filters:
            query = build_where(dataset.filters, query, table_dict)
        if dataset.joins:
            query = build_joins(dataset.joins, query, table_dict)
    return query
'''


def build_count_query_for_subject(console_subject):
    dataset = console_subject.dataset
    query =None
    if dataset is not None:
        query = _from(dataset.columns[0])
        query = query.select(fn.Count("*"))
        for join in dataset.joins:
            query = _join(query, join)
        if dataset.filters:
            query = _filter(query, dataset.filters)
    return query


def get_graphic(graphics, chart_id):
    for chart in graphics:
        if chart.chartId == chart_id:
            return chart

'''
def build_query_for_subject_chart(subject_id, chart_id):
    console_subject = load_console_subject_by_id(subject_id)
    chart = get_graphic(console_subject.graphics, chart_id)
    query = Query._builder()
    topic = get_topic_by_id(chart.indicators[0].topicId)
    t = Table(build_collection_name(topic.name))
    q = query.from_(t)
    for indicator in chart.indicators:
        topic = get_topic_by_id(indicator.topicId)
        indicator_factor = get_factor(indicator.factorId, topic)
        if indicator.aggregator == "sum":
            q = q.select(fn.Sum(t[indicator_factor.name]))
        elif indicator.aggregator == "avg":
            q = q.select(fn.Avg(t[indicator_factor.name]))
        elif indicator.aggregator == "max":
            q = q.select(fn.Max(t[indicator_factor.name]))
        elif indicator.aggregator == "min":
            q = q.select(fn.Min(t[indicator_factor.name]))
        else:
            q = q.select(fn.Max(t[indicator_factor.name]))

    for dimension in chart.dimensions:
        topic = get_topic_by_id(dimension.topicId)
        dimension_factor = get_factor(dimension.factorId, topic)
        q = q.select(dimension_factor.name)
        q = q.groupby(t[dimension_factor.name])

    return q
'''


def build_query_for_subject_chart(chart_id):
    console_subject = load_console_subject_by_report_id(chart_id)
    columns_dict = column_list_convert_dict(console_subject.dataset.columns)
    chart = load_report_by_id(chart_id)

    q = Query._builder()
    topic = get_topic_by_id(columns_dict.get(chart.indicators[0].columnId).parameter.topicId)
    t = Table(build_collection_name(topic.name))
    q = q.from_(t)
    for indicator in chart.indicators:
        q = _indicator(q, indicator, columns_dict.get(indicator.columnId))

    for dimension in chart.dimensions:
        q = _groupby(q, columns_dict.get(dimension.columnId))



    return q


def column_list_convert_dict(columns) -> dict:
    columns_dict={}
    for column in columns:
        columns_dict[column.columnId] = column
    return columns_dict
