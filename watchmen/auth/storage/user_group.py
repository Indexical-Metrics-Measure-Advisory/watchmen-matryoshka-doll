from bson import regex

from watchmen.auth.user_group import UserGroup
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN

db = get_client(WATCHMEN)
user_groups = db.get_collection('user_groups')


def create_user_group_storage(user_group: UserGroup):
    user_group.userGroupId = get_surrogate_key()
    if type(user_group) is not dict:
        user_group = user_group.dict()
    user_groups.insert_one(user_group)
    return user_group["userGroupId"]


def query_user_groups_by_name_with_paginate(query_name: str, pagination: Pagination):
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    result = user_groups.find({"name": regex.Regex(query_name)}).skip(skips).limit(pagination.pageSize)
    return list(result)
