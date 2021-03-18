import pymongo
from bson import regex

from watchmen.common.pagination import Pagination
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.enum.model.enum import Enum

ENUMS = "enums"

template = find_template()


def save_enum_to_storage(enum: Enum):
    if check_fake_id(enum.enumId):
        template.create(ENUMS, enum, Enum)
    else:
        template.update_one(ENUMS, {"enumId": enum.enumId}, enum, Enum)


def load_enum_by_id(enum_id):
    template.find_one(ENUMS, {"enumId": enum_id}, Enum)


def load_enum_list_by_name(enum_name):
    return template.find(ENUMS, {"name": regex.Regex(enum_name)}, Enum)


def load_all_enum_list(pagination: Pagination):
    return template.query_with_pagination(ENUMS, pagination, Enum, sort_dict={"last_modified": pymongo.DESCENDING})


def query_enum_list_with_pagination(query_name: str, pagination: Pagination):
    return template.query_with_pagination(ENUMS, pagination, Enum, query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])
