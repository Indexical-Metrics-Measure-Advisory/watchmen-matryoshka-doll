from bson import regex

from watchmen.auth.user_group import UserGroup
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.common.utils.data_utils import check_fake_id

USER_GROUPS = "user_groups"

template = find_template()


def get_user_group(user_group_id):
    return template.find_one(USER_GROUPS, {"userGroupId": user_group_id}, UserGroup)


def get_user_group_list_by_ids(user_group_ids: list):

    return template.find(USER_GROUPS, {"userGroupId": {"$in": user_group_ids}}, UserGroup)


def load_group_list_by_name(query_name):

    return template.find(USER_GROUPS, {"name": regex.Regex(query_name)}, UserGroup)


def create_user_group_storage(user_group: UserGroup):
    if user_group.userGroupId is None or check_fake_id(user_group.userGroupId):
        user_group.userGroupId = get_surrogate_key()
    return template.create(USER_GROUPS, user_group, UserGroup)


def update_user_group_storage(user_group: UserGroup):
    return template.update_one(USER_GROUPS, {"userGroupId": user_group.userGroupId}, user_group, UserGroup)


def query_user_groups_by_name_with_paginate(query_name: str, pagination: Pagination):
    return template.query_with_pagination(USER_GROUPS, pagination, UserGroup, {"name": regex.Regex(query_name)})


def import_user_group_to_db(group):
    return template.create(USER_GROUPS, group, UserGroup)
