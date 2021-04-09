from typing import List

from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.storage_template import upsert_, find_by_id, insert_one, update_one, find_one, find_, \
    page_, page_all, list_all
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.enum.model.enum import Enum, EnumItem

ENUMS = "enums"

ENUM_ITEMS = "enum_items"


# template = find_template()


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
        # template.create_or_update(ENUM_ITEMS, {"itemId": item.itemId}, item, EnumItem)
        upsert_({"itemId": item.itemId}, item, EnumItem, ENUM_ITEMS)


def load_enum_items_by_enum_id(enum_id) -> List[EnumItem]:
    # return template.find(ENUM_ITEMS, {"enumId": enum_id}, EnumItem)
    return find_by_id(enum_id, EnumItem, ENUM_ITEMS)


def save_enum_to_storage(enum: Enum):
    if check_fake_id(enum.enumId):
        enum.enumId = get_surrogate_key()
        items_copy = enum.items.copy()
        enum.items = []
        # result = template.create(ENUMS, enum, Enum)
        result = insert_one(enum, Enum, ENUMS)
        items = __add_enum_id(items_copy, result.enumId)
        save_enum_items_to_storage(items)
        return result
    else:
        items_copy = enum.items.copy()
        enum.items = []
        items = __add_enum_id(items_copy, enum.enumId)
        save_enum_items_to_storage(items)
        # return template.update_one(ENUMS, {"enumId": enum.enumId}, enum, Enum)
        return update_one(enum, Enum, ENUMS)


def load_enum_by_id(enum_id) -> Enum:
    # result = template.find_one(ENUMS, {"enumId": enum_id}, Enum)
    result = find_by_id(enum_id, Enum, ENUMS)
    result.items = load_enum_items_by_enum_id(enum_id)
    return result


def load_enum_by_parent_id(parent_id) -> Enum:
    # result = template.find_one(ENUMS, {"parentEnumId": parent_id}, Enum)
    result = find_one({"parentEnumId": parent_id}, Enum, ENUMS)
    if result is not None:
        result.items = load_enum_items_by_enum_id(result.enumId)
        return result or []


def load_enum_list_by_name(enum_name) -> List[Enum]:
    # return template.find(ENUMS, {"name": regex.Regex(enum_name)}, Enum)
    return find_({"name": {"like": enum_name}}, Enum, ENUMS)


def load_all_enum_list(pagination: Pagination) -> DataPage:
    # return template.query_with_pagination(ENUMS, pagination, Enum, sort_dict={"last_modified": pymongo.DESCENDING})
    return page_all([("last_modified", "desc")], pagination, Enum, ENUMS)


def query_enum_list_with_pagination(query_name: str, pagination: Pagination) -> DataPage:
    '''
    return template.query_with_pagination(ENUMS, pagination, Enum, query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])
    '''
    return page_({"name": {"like": query_name}}, [("last_modified", "desc")], pagination, Enum, ENUMS)


def load_enum_list():
    # return template.find_all(ENUMS, Enum)
    return list_all(Enum, ENUMS)
