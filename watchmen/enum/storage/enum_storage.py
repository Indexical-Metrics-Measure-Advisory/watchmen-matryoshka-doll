from typing import List

import pymongo
from bson import regex

from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.enum.model.enum import Enum, EnumItem

ENUMS = "enums"

ENUM_ITEMS = "enum_items"

template = find_template()


def __add_enum_id(items: List[EnumItem], enum_id):
    result = []
    for item in items:
        item.enumId = enum_id
        result.append(item)
    return result


def save_enum_items_to_storage(items: List[EnumItem]):
    for item in items:
        if item.itemId is None or check_fake_id(item.itemId):
            item.itemId = get_surrogate_key()
        template.create_or_update(ENUM_ITEMS, {"itemId": item.itemId}, item, EnumItem)


def load_enum_items_by_enum_id(enum_id) -> List[EnumItem]:
    return template.find(ENUM_ITEMS, {"enumId": enum_id}, EnumItem)


def save_enum_to_storage(enum: Enum):
    if check_fake_id(enum.enumId):
        enum.enumId= get_surrogate_key()
        items_copy = enum.items.copy()
        enum.items = []
        result = template.create(ENUMS, enum, Enum)
        items = __add_enum_id(items_copy, result.enumId)
        save_enum_items_to_storage(items)
        return result
    else:
        items_copy = enum.items.copy()
        enum.items = []
        items = __add_enum_id(items_copy, enum.enumId)
        save_enum_items_to_storage(items)
        return template.update_one(ENUMS, {"enumId": enum.enumId}, enum, Enum)


def load_enum_by_id(enum_id)->Enum:
    result = template.find_one(ENUMS, {"enumId": enum_id}, Enum)
    result.items = load_enum_items_by_enum_id(enum_id)
    return result


def load_enum_by_parent_id(parent_id)->Enum:
    result = template.find_one(ENUMS, {"parentEnumId": parent_id}, Enum)
    if result is not None:
        result.items = load_enum_items_by_enum_id(result.enumId)
        return result or []


def load_enum_list_by_name(enum_name)->List[Enum]:
    return template.find(ENUMS, {"name": regex.Regex(enum_name)}, Enum)


def load_all_enum_list(pagination: Pagination)->DataPage:
    return template.query_with_pagination(ENUMS, pagination, Enum, sort_dict={"last_modified": pymongo.DESCENDING})


def query_enum_list_with_pagination(query_name: str, pagination: Pagination)->DataPage:
    return template.query_with_pagination(ENUMS, pagination, Enum, query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])


def load_enum_list():
    return template.find_all(ENUMS,Enum)
