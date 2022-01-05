
import logging
from typing import List
from pypika import AliasedQuery

from watchmen.common.presto.presto_client import get_connection
from watchmen.report.builder.consume_filter import build_indicators, build_where
from watchmen.report.builder.dialects import PrestoQuery
from watchmen.report.engine.dataset_engine import build_query_for_subject
from watchmen.report.model.consume_model import Indicator, Where

log = logging.getLogger("app." + __name__)


def build_query_for_consume(console_subject, indicators: List[Indicator], where_: Where, current_user):
    dataset_query = build_query_for_subject(console_subject, current_user)
    dataset_query_alias = "consume_dataset"
    consume_query = PrestoQuery.with_(dataset_query, dataset_query_alias).from_(AliasedQuery(dataset_query_alias))
    if indicators:
        _select, _groupby = build_indicators(indicators, dataset_query_alias)
        consume_query = consume_query.select(*_select).groupby(*_groupby)
    else:
        consume_query = consume_query.select("*")
    if where_:
        filter_ = build_where(where_, dataset_query_alias)
        consume_query = consume_query.where(filter_)
    query_sql = consume_query.get_sql()
    log.info("sql:{0}".format(query_sql))
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query_sql)
    rows = cur.fetchall()
    return rows
