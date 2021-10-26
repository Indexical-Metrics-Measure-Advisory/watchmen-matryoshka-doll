import logging
import time
import traceback

from pypika import functions as fn, AliasedQuery, Field, JoinType

from watchmen.common.pagination import Pagination
from watchmen.common.presto.presto_client import get_connection
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_id
from watchmen.monitor.model.query_monitor import QueryMonitor
from watchmen.monitor.services.query_monitor_service import build_query_summary, \
    build_result_summary, build_query_monitor
from watchmen.pipeline.utils.units_func import get_factor
from watchmen.report.builder.dataset_filter import build_dataset_where, build_dataset_select_fields
from watchmen.report.builder.dialects import PrestoQuery, PrestoQueryBuilder
from watchmen.report.builder.space_filter import get_topic_sub_query_with_space_filter
from watchmen.report.builder.utils import build_table_by_topic_id
from watchmen.report.engine.sql_builder import _filter
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

log = logging.getLogger("app." + __name__)


def __find_factor_index(field_list, factor_name_list):
    index_list = []
    for factor_name in factor_name_list:
        for i in range(len(field_list)):
            field = field_list[i]
            if field[0] == factor_name:
                index_list.append(i)
    return index_list


def get_factor_value_by_subject_and_condition(console_subject, factor_name_list, filter_list, current_user):
    query = build_query_for_subject(console_subject, current_user)
    if filter_list:
        query = _filter(query, filter_list)
    conn = get_connection()
    cur = conn.cursor()
    sql = query.get_sql()

    cur.execute(sql)
    rows = cur.fetchall()

    index_list = __find_factor_index(cur.description, factor_name_list)
    results = []
    if index_list:
        for rw in rows:
            row_data = []
            for index in index_list:
                row_data.append(rw[index])
            results.append(row_data)
        return results
    else:
        raise KeyError("factor_name :{0} can't find in subject {1}".format(factor_name_list, console_subject.name))


async def load_dataset_by_subject_id(subject_id, pagination: Pagination, current_user):
    console_subject = load_console_subject_by_id(subject_id, current_user)
    query_monitor: QueryMonitor = build_query_monitor(console_subject, query_type="dataset")
    try:
        # build query condition
        start = time.time()
        count_query = build_count_query_for_subject(console_subject, current_user)
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
        query = build_query_for_subject(console_subject, current_user)
        # query_sql = build_page_by_row_number(pagination, query)
        query_sql = build_pagination(query.get_sql(), pagination)
        query_summary = build_query_summary(query_sql)
        log.info("sql:{0}".format(query_sql))
        print(query_sql)
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


def __remove_index(rows):
    # results = []
    for row in rows:
        del row[0]
    return rows


def build_pagination(query: str, pagination):
    offset = pagination.pageSize * (pagination.pageNumber - 1)
    # todo, need higher presto or trino engine to support offset
    return query + f' OFFSET {offset} LIMIT {pagination.pageSize}'
    # return query.limit(pagination.pageSize)


async def save_query_monitor_data(query_monitor):
    pass  ## TODO save_query_monitor_data
    # await sync_query_monitor_data(query_monitor)


def build_query_for_subject(console_subject, current_user):
    return build_dataset_query_for_subject(console_subject, current_user)


def build_count_query_for_subject(console_subject, current_user):
    return build_dataset_query_for_subject(console_subject, current_user, True)


def build_dataset_query_for_subject(console_subject, current_user, for_count=False):
    dataset = console_subject.dataset
    if dataset is None:
        return None

    topic_space_filter = get_topic_sub_query_with_space_filter(console_subject, current_user)

    if dataset.joins and len(dataset.joins) > 0:
        topic_id = dataset.joins[0].topicId
        topic_table = topic_space_filter(topic_id)
        if topic_table:
            q = PrestoQuery.with_(topic_table["query"], topic_table["alias"]).from_(topic_table["alias"])
        else:
            table = build_table_by_topic_id(topic_id)
            q = PrestoQuery.from_(table)
    else:
        topic_id = dataset.columns[0].parameter.topicId
        topic_table = topic_space_filter(topic_id)
        if topic_table:
            table = AliasedQuery(topic_table["alias"])
            q = PrestoQuery.with_(topic_table["query"], topic_table["alias"]).from_(table)
        else:
            table = build_table_by_topic_id(topic_id)
            q = PrestoQuery.from_(table)

    for join in dataset.joins:
        right_topic_id = join.secondaryTopicId
        right_topic = get_topic_by_id(right_topic_id)
        right_topic_table = topic_space_filter(right_topic_id)
        if right_topic_table:
            q = q.with_(right_topic_table["query"], right_topic_table["alias"])
            right_table = AliasedQuery(right_topic_table["alias"])
        else:
            right_table = build_table_by_topic_id(right_topic_id)

        left_topic_id = join.topicId
        left_topic = get_topic_by_id(left_topic_id)
        left_topic_table = topic_space_filter(left_topic_id)
        if left_topic_table:
            left_table = AliasedQuery(left_topic_table["alias"])
        else:
            left_table = build_table_by_topic_id(right_topic_id)

        left_factor = get_factor(join.factorId, left_topic)
        left_field = Field(left_factor.name, None, left_table)

        right_factor = get_factor(join.secondaryFactorId, right_topic)
        right_field = Field(right_factor.name, None, right_table)

        if join.type == "inner" or join.type == "":
            join_type = JoinType.inner
        elif join.type == "left":
            join_type = JoinType.left
        elif join.type == "right":
            join_type = JoinType.right
        else:
            join_type = JoinType.inner

        q = q.join(right_table, join_type).on(left_field.eq(right_field))

    q = q.where(build_dataset_where(dataset.filters, topic_space_filter))
    if for_count:
        return q.select(fn.Count("*"))
    else:
        return q.select(*build_dataset_select_fields(dataset.columns, topic_space_filter))
