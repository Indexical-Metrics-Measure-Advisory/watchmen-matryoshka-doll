import logging

from watchmen.common.constants import presto_constants
from watchmen.common.constants.parameter_constants import RAW
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name, is_presto_varchar_type, is_presto_int_type, \
    is_presto_datetime
from watchmen.pipeline.single.stage.unit.utils.units_func import BOOLEAN, NUMBER, TIME
from watchmen.topic.factor.factor import Factor
from watchmen.topic.topic import Topic

db = get_client()

collection = db.get_collection('_schema')

log = logging.getLogger("app." + __name__)


def remove_presto_schema_by_name(topic_name):
    try:
        collection.delete_one({"table": build_collection_name(topic_name)})
    except Exception as e:
        log.exception(e)


def __convert_presto_type(factor_type):
    if is_presto_varchar_type(factor_type):
        return presto_constants.VARCHAR
    elif is_presto_int_type(factor_type):
        return presto_constants.INTEGER
    elif factor_type == BOOLEAN:
        return presto_constants.BOOLEAN
    elif is_presto_datetime(factor_type):
        return presto_constants.DATE
    elif factor_type == TIME:
        return presto_constants.TIMESTAMP
    elif factor_type == NUMBER or factor_type:
        return presto_constants.DECIMAL
    else:
        return presto_constants.VARCHAR


def __build_presto_fields(factors):
    presto_fields = [{"name": "_id", "type": "ObjectId", "hidden": True},
                     {"name": "insert_time", "type": "timestamp", "hidden": False},
                     {"name": "update_time", "type": "timestamp", "hidden": False}]
    for factor in factors:
        factor = Factor.parse_obj(factor)
        field = {"name": factor.name, "type": __convert_presto_type(factor.type), "hidden": False}
        presto_fields.append(field)

    return presto_fields


def create_or_update_presto_schema_fields(topic: Topic):
    if topic.type == RAW:
        log.info("raw topic ignore presto update")
    else:
        topic_name = build_collection_name(topic.name)
        presto_schema = collection.find_one({"table": topic_name})
        new_schema = {"table": topic_name, "fields": __build_presto_fields(topic.factors)}
        if presto_schema is None:
            collection.insert(new_schema)
        else:
            collection.delete_one({"table": topic_name})
            collection.insert(new_schema)
