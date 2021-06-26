import logging

from pydantic import Field
from pydantic.main import BaseModel

from watchmen.common.constants import presto_constants
from watchmen.common.constants.parameter_constants import RAW
from watchmen.database.storage.storage_template import find_one, insert_one, delete_one
from watchmen.common.utils.data_utils import build_collection_name, is_presto_varchar_type, is_presto_int_type, \
    is_presto_datetime
from watchmen.config.config import settings
from watchmen.pipeline.single.stage.unit.utils.units_func import BOOLEAN, NUMBER, TIME
from watchmen.topic.factor.factor import Factor
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


class Schema(BaseModel):
    table: str = ""
    field_list: list = Field([], alias="fields")


def remove_presto_schema_by_name(topic_name):
    try:
        delete_one({"table": build_collection_name(topic_name)}, "_schema")
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
    elif factor_type == NUMBER:
        return settings.DECIMAL
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
    if settings.STORAGE_ENGINE == "mongo":
        create_or_update_presto_schema_fields_for_mongo(topic)


def create_or_update_presto_schema_fields_for_mongo(topic: Topic):
    if topic.type == RAW:
        log.info("raw topic ignore presto update")
    else:
        topic_name = build_collection_name(topic.name)
        presto_schema = find_one({"table": topic_name}, Schema, "_schema")
        new_schema = {"table": topic_name, "fields": __build_presto_fields(topic.factors)}
        if presto_schema is None:
            insert_one(new_schema, Schema, "_schema")
        else:
            delete_one({"table": topic_name}, "_schema")
            insert_one(new_schema, Schema, "_schema")
