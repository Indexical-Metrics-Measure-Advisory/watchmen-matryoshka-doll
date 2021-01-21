from pypika import Query, Table
from pypika import functions as fn

from watchmen.common.pagination import Pagination
from watchmen.common.presto.presto_client import get_connection
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_id
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def build_columns(columns):
    topic_dict = {}

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
    for key, items in topic_dict.items():
        t = Table(key)
        q = q.from_(Table(key))
        for item in items:
            q = q.select(t[item])

    return q


def build_joins(joins, query):
    return query


def load_dataset_by_subject_id(subject_id, pagination: Pagination):
    console_subject = load_console_subject_by_id(subject_id)

    # print(console_subject.json())
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


def build_where(filters, query):
    # for filter in filters:
    #     pas s

    return query


def build_query_for_subject(console_subject):
    dataset = console_subject.dataset
    # query =None
    if dataset is not None:
        # build columns
        if len(dataset.columns) > 0:
            query = build_columns(dataset.columns)
        if len(dataset.filters) > 0:
            query = build_where(dataset.filters, query)
        if len(dataset.joins) > 0:
            query = build_joins(dataset.joins, query)
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
