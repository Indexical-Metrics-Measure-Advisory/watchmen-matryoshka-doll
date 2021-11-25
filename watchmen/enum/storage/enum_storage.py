from typing import List

from model.model.common.data_page import DataPage
from model.model.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.database.find_storage_template import find_storage_template
from model.model.enum.enum import Enum

ENUMS = "enums"

ENUM_ITEMS = "enum_items"


# template = find_template()

storage_template = find_storage_template()


def save_enum_to_storage(enum: Enum):
    if check_fake_id(enum.enumId):
        enum.enumId = get_surrogate_key()
        # enum.items = []
        # result = template.create(ENUMS, enum, Enum)
        result = storage_template.insert_one(enum, Enum, ENUMS)
        # items = __add_enum_id(items_copy, result.enumId)
        # save_enum_items_to_storage(items_copy, enum.name)
        return result
    else:
        # items_copy = enum.items.copy()
        # # enum.items = []
        # # items = __add_enum_id(items_copy, enum.enumId)
        # save_enum_items_to_storage(items_copy, enum.name)
        # # return template.update_one(ENUMS, {"enumId": enum.enumId}, enum, Enum)
        return storage_template.update_one(enum, Enum, ENUMS)


def load_enum_by_id(enum_id, current_user) -> Enum:
    # result = template.find_one(ENUMS, {"enumId": enum_id}, Enum)
    enum = storage_template.find_one({"and": [{"enumId": enum_id}, {"tenantId": current_user.tenantId}]}, Enum, ENUMS)
    # enum.items = load_enum_items_by_enum_name(enum.name, current_user)
    return enum


def load_enum_by_parent_id(parent_id, current_user) -> Enum:
    # result = template.find_one(ENUMS, {"parentEnumId": parent_id}, Enum)
    result = storage_template.find_one({"and": [{"parentEnumId": parent_id}, {"tenantId": current_user.tenantId}]}, Enum, ENUMS)
    # if result is not None:
    #     result.items = load_enum_items_by_enum_name(result.name, current_user)
    return result or []


def load_enum_list_by_name(enum_name, current_user) -> List[Enum]:
    # return template.find(ENUMS, {"name": regex.Regex(enum_name)}, Enum)
    return storage_template.find_({"and": [{"name": {"like": enum_name}}, {"tenantId": current_user.tenantId}]}, Enum, ENUMS)


def load_all_enum_list(pagination: Pagination, current_user) -> DataPage:
    # return template.query_with_pagination(ENUMS, pagination, Enum, sort_dict={"last_modified": pymongo.DESCENDING})
    return storage_template.page_({"tenantId": current_user.tenantId}, [("last_modified", "desc")], pagination, Enum, ENUMS)


def query_enum_list_with_pagination(query_name: str, pagination: Pagination, current_user) -> DataPage:
    '''
    return template.query_with_pagination(ENUMS, pagination, Enum, query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])
    '''
    return storage_template.page_({"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]},
                 [("lastmodified", "desc")], pagination, Enum, ENUMS)


def load_enum_list(current_user):
    # return template.find_all(ENUMS, Enum)
    return storage_template.find_({"tenantId": current_user.tenantId}, Enum, ENUMS)
