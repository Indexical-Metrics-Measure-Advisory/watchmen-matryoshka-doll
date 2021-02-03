import math
# import os
from enum import Enum

from pydantic.tools import lru_cache

from watchmen.common.data_page import DataPage

WATCHMEN = "watchmen"


@lru_cache(maxsize=100)
def build_collection_name(topic_name):
    return "topic_" + topic_name


def is_field_value(value):
    return type(value) != dict and type(value) != list


def get_dict_schema_set(model_schema_set):
    result = {}
    for schema in model_schema_set.schemas.values():
        result[schema.modelId] = schema
    return result


def get_dict_relationship(model_schema_set):
    result = {}
    for relationship in model_schema_set.relationships.values():
        if relationship.parentId in result.keys():
            result[relationship.parentId].append(relationship)
        else:
            result[relationship.parentId] = []
            result[relationship.parentId].append(relationship)
    return result


class RelationshipType(Enum):
    OneToOne = "OneToOne"
    OneToMany = "OneToMany"
    ManyToMany = "ManyToMany"


def build_data_pages(pagination, result, item_count):
    data_page = DataPage()
    data_page.data = result
    data_page.itemCount = item_count
    data_page.pageSize = pagination.pageSize
    data_page.pageNumber = pagination.pageNumber
    data_page.pageCount = math.ceil(item_count / pagination.pageSize)
    return data_page
