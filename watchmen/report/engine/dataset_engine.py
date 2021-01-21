import operator

from pypika import Query, Table, JoinType
from pypika import functions as fn

from watchmen.common.pagination import Pagination
from watchmen.common.presto.presto_client import get_connection
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_id
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def build_columns(columns):
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
        joins_data_list.append((table,operator.eq(secondary_table[secondary_factor.name],table[factor.name]),join_type))

    print(joins_data_list)
    return _add_joins(joins_data_list,query)


def load_dataset_by_subject_id(subject_id, pagination: Pagination):
    console_subject = load_console_subject_by_id(subject_id)

    query = build_query_for_subject(console_subject)
    conn = get_connection()
    print("sql:", query.get_sql())
    cur = conn.cursor()
    cur.execute(query.get_sql())
    rows = cur.fetchall()
    print("sql result:", rows)
    return rows


def load_chart_dataset(subject_id, chart_id):
    query = build_query_for_subject_chart(subject_id, chart_id)
    conn = get_connection()
    print("sql:", query.get_sql())
    cur = conn.cursor()
    cur.execute(query.get_sql())
    rows = cur.fetchall()
    print("sql result:", rows)
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


def build_query_for_subject(console_subject):
    dataset = console_subject.dataset
    # query =None
    if dataset is not None:
        # build columns
        if  dataset.columns:
            query, table_dict = build_columns(dataset.columns)
        if  dataset.filters:
            query = build_where(dataset.filters, query, table_dict)
        if  dataset.joins :
            query = build_joins(dataset.joins, query, table_dict)
    return query


def get_graphic(graphics, chart_id):
    for chart in graphics:
        if chart.chartId == chart_id:
            return chart


def build_query_for_subject_chart(subject_id, chart_id):
    console_subject = load_console_subject_by_id(subject_id)
    chart = get_graphic(console_subject.graphics, chart_id)

    query = Query._builder()
    for indicator in chart.indicators:
        topic = get_topic_by_id(indicator.topicId)
        factor = get_factor(indicator.factorId, topic)
        t = Table(build_collection_name(topic.name))
        q = query.from_(t)
        if indicator.aggregator == "sum":
            q = q.select(fn.Sum(t[factor.name]))
        elif indicator.aggregator == "avg":
            q = q.select(fn.Avg(t[factor.name]))
        elif indicator.aggregator == "max":
            q = q.select(fn.Max(t[factor.name]))
        elif indicator.aggregator == "min":
            q = q.select(fn.Min(t[factor.name]))

    for dimension in chart.dimensions:
        topic = get_topic_by_id(dimension.topicId)
        factor = get_factor(dimension.factorId, topic)
        q = q.groupby(t[factor.name])

    return q

