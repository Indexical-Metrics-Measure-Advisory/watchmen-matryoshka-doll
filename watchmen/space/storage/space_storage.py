from bson import regex

from watchmen.common.mongo import mongo_template
from watchmen.common.pagination import Pagination
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.space.space import Space

template = find_template()


def insert_space_to_storage(space):
    return template.create("spaces", space, Space)


def get_space_by_id(space_id: str):
    return template.find_one("spaces", {"spaceId": space_id}, Space)


def update_space_to_storage(space_id: str, space: Space):
    return template.update_one("spaces", {"spaceId": space_id}, space, Space)


def query_space_with_pagination(query_name: str, pagination: Pagination):
    return template.query_with_pagination("spaces", pagination, Space, {"name": regex.Regex(query_name)})


def get_space_list_by_ids(space_ids):
    return template.find("spaces", {"spaceId": {"$in": space_ids}}, Space)


def load_space_by_user(group_ids):
    return template.find("spaces", {"groupIds": {"$in": group_ids}}, Space)


def load_space_by_name(name):
    return mongo_template.find("spaces", {"name": name}, Space)


def load_space_list_by_name(name):
    return mongo_template.find("spaces", {"name": regex.Regex(name)}, Space)


def load_space_list_by_user_id_with_pagination(group_ids, pagination: Pagination):
    return mongo_template.query_with_pagination("spaces", {"groupIds": {"$in": group_ids}}, pagination, Space)


def import_space_to_db(space):
    return mongo_template.create("spaces", space, Space)
