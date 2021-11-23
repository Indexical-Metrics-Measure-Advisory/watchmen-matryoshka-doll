from typing import List

from watchmen.auth.user_group import UserGroup
from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.database.find_storage_template import find_storage_template

USER_GROUPS = "user_groups"

storage_template = find_storage_template()


def get_user_group(user_group_id, current_user) -> UserGroup:
    return storage_template.find_one({"and": [{"userGroupId": user_group_id}, {"tenantId": current_user.tenantId}]}, UserGroup,
                    USER_GROUPS)


def get_user_group_list_by_ids(user_group_ids: list, current_user) -> List[UserGroup]:
    if user_group_ids:
        return storage_template.find_({"and": [{"userGroupId": {"in": user_group_ids}}, {"tenantId": current_user.tenantId}]}, UserGroup,
                     USER_GROUPS)
    else:
        return []


def load_group_list_by_name(query_name, current_user) -> List[UserGroup]:
    return storage_template.find_({"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]}, UserGroup, USER_GROUPS)


def get_user_group_by_name(name, current_user):
    return storage_template.find_one({"and": [{"name": name}, {"tenantId": current_user.tenantId}]}, UserGroup, USER_GROUPS)


def create_user_group_storage(user_group: UserGroup) -> UserGroup:
    if user_group.userGroupId is None or check_fake_id(user_group.userGroupId):
        user_group.userGroupId = get_surrogate_key()
    return storage_template.insert_one(user_group, UserGroup, USER_GROUPS)


def update_user_group_storage(user_group: UserGroup) -> UserGroup:

    return storage_template.update_one(user_group, UserGroup, USER_GROUPS)


def query_user_groups_by_name_with_paginate(query_name: str, pagination: Pagination, current_user) -> DataPage:

    return storage_template.page_({"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]}, [("name", "desc")],
                 pagination, UserGroup, USER_GROUPS)


def import_user_group_to_db(group) -> UserGroup:

    return storage_template.insert_one(group, UserGroup, USER_GROUPS)
