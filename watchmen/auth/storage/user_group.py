from bson import regex

from watchmen.auth.user_group import UserGroup
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_data_pages, check_fake_id

db = get_client()
user_groups = db.get_collection('user_groups')


def get_user_group(user_group_id):
    return user_groups.find_one({"userGroupId": user_group_id})


def get_user_group_list_by_ids(user_group_ids: list):
    result = user_groups.find({"userGroupId": {"$in": user_group_ids}})
    return list(result)


def load_group_list_by_name(query_name):
    result = user_groups.find({"name": regex.Regex(query_name)})
    return list(result)


def create_user_group_storage(user_group: UserGroup):
    if user_group.userGroupId is None or check_fake_id(user_group.userGroupId):
        user_group.userGroupId = get_surrogate_key()
    if type(user_group) is not dict:
        user_group = user_group.dict()
    user_groups.insert_one(user_group)
    return user_group


def update_user_group_storage(user_group: UserGroup):
    user_groups.update_one({"userGroupId": user_group.userGroupId}, {"$set": user_group.dict()})
    return user_group


def query_user_groups_by_name_with_paginate(query_name: str, pagination: Pagination):
    items_count = user_groups.find({"name": regex.Regex(query_name)}).count()
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    result = user_groups.find({"name": regex.Regex(query_name)}).skip(skips).limit(pagination.pageSize)
    return build_data_pages(pagination, list(result), items_count)
