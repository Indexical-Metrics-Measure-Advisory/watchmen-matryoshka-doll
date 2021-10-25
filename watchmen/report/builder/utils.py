from decimal import Decimal

from pypika import Table, Schema
from pypika.terms import LiteralValue

from watchmen.common.utils.data_utils import build_collection_name
from watchmen.database.datasource.data_source import DataSource
from watchmen.database.datasource.storage.data_source_storage import load_data_source_by_id
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def transform_value_str_to_number(value_):
    if isinstance(value_, str):
        if value_.lstrip('-').isdigit():
            return Decimal(value_)


def build_table_by_topic_id(topic_id) -> Table:
    topic = get_topic_by_id(topic_id)
    topic_col_name = build_collection_name(topic.name)
    datasource: DataSource = load_data_source_by_id(topic.dataSourceId)
    catalog_name = datasource.dataSourceCode
    schema_name = datasource.name
    schema = Schema(schema_name, LiteralValue(catalog_name))
    return Table(topic_col_name, schema)





