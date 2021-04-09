from typing import List

from watchmen.auth.user_group import UserGroup
from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.storage_template import find_one, find_, insert_one, page_, update_one
from watchmen.common.utils.data_utils import check_fake_id

USER_GROUPS = "user_groups"


# template = find_template()


def get_user_group(user_group_id) -> UserGroup:
    # return template.find_one(USER_GROUPS, {"userGroupId": user_group_id}, UserGroup)
    return find_one({"userGroupId": user_group_id}, UserGroup, USER_GROUPS)


def get_user_group_list_by_ids(user_group_ids: list) -> List[UserGroup]:
    # return template.find(USER_GROUPS, {"userGroupId": {"$in": user_group_ids}}, UserGroup)
    return find_({"userGroupId": {"in": user_group_ids}}, UserGroup, USER_GROUPS)


def load_group_list_by_name(query_name) -> List[UserGroup]:
    # return template.find(USER_GROUPS, {"name": regex.Regex(query_name)}, UserGroup)
    return find_({"name": {"like": query_name}}, UserGroup, USER_GROUPS)


def create_user_group_storage(user_group: UserGroup) -> UserGroup:
    if user_group.userGroupId is None or check_fake_id(user_group.userGroupId):
        user_group.userGroupId = get_surrogate_key()
    # return template.create(USER_GROUPS, user_group, UserGroup)
    return insert_one(user_group, UserGroup, USER_GROUPS)


def update_user_group_storage(user_group: UserGroup) -> UserGroup:
    # return template.update_one(USER_GROUPS, {"userGroupId": user_group.userGroupId}, user_group, UserGroup)
    return update_one(user_group, UserGroup, USER_GROUPS)


def query_user_groups_by_name_with_paginate(query_name: str, pagination: Pagination) -> DataPage:
    # return template.query_with_pagination(USER_GROUPS, pagination, UserGroup, {"name": regex.Regex(query_name)})
    return page_({"name": {"like": query_name}}, [("name", "desc")], pagination, UserGroup, USER_GROUPS)


def import_user_group_to_db(group) -> UserGroup:
    # return template.create(USER_GROUPS, group, UserGroup)
    return insert_one(group, UserGroup, USER_GROUPS)
