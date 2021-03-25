from typing import List

from bson import regex

from watchmen.common.data_page import DataPage
from watchmen.common.mongo import mongo_template
from watchmen.common.pagination import Pagination
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.space.space import Space

SPACES = "spaces"

template = find_template()


def insert_space_to_storage(space) -> Space:
    return template.create(SPACES, space, Space)


def get_space_by_id(space_id: str) -> Space:
    return template.find_one(SPACES, {"spaceId": space_id}, Space)


def update_space_to_storage(space_id: str, space: Space) -> Space:
    return template.update_one(SPACES, {"spaceId": space_id}, space, Space)


def query_space_with_pagination(query_name: str, pagination: Pagination) -> DataPage:
    return template.query_with_pagination(SPACES, pagination, Space, {"name": regex.Regex(query_name)})


def get_space_list_by_ids(space_ids) -> List[Space]:
    return template.find(SPACES, {"spaceId": {"$in": space_ids}}, Space)


def load_space_by_user(group_ids) -> List[Space]:
    return template.find(SPACES, {"groupIds": {"$in": group_ids}}, Space)


def load_space_by_name(name) -> List[Space]:
    return mongo_template.find(SPACES, {"name": name}, Space)


def load_space_list_by_name(name) -> List[Space]:
    return mongo_template.find(SPACES, {"name": regex.Regex(name)}, Space)


def load_space_list_by_user_id_with_pagination(group_ids, pagination: Pagination) -> DataPage:
    return mongo_template.query_with_pagination(SPACES, {"groupIds": {"$in": group_ids}}, pagination, Space)


def import_space_to_db(space) -> Space:
    return mongo_template.create(SPACES, space, Space)
