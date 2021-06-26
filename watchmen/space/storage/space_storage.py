from typing import List

from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.database.storage.storage_template import insert_one, find_by_id, update_one, page_, find_, find_one
from watchmen.space.space import Space

SPACES = "spaces"


def insert_space_to_storage(space) -> Space:
    return insert_one(space, Space, SPACES)


def get_space_by_id(space_id: str) -> Space:
    return find_by_id(space_id, Space, SPACES)


def update_space_to_storage(space_id: str, space: Space) -> Space:
    return update_one(space, Space, SPACES)


def query_space_with_pagination(query_name: str, pagination: Pagination) -> DataPage:
    return page_({"name": {"like": query_name}}, [("name", "desc")], pagination, Space, SPACES)


def get_space_list_by_ids(space_ids) -> List[Space]:
    if space_ids:
        return find_({"spaceId": {"in": space_ids}}, Space, SPACES)
    else:
        return []


def load_space_by_user(group_ids) -> List[Space]:
    if group_ids:
        return find_({"groupIds": {"in": group_ids}}, Space, SPACES)
    else:
        return []


def load_space_by_name(name) -> Space:
    return find_one({"name": name}, Space, SPACES)


def load_space_list_by_name(name) -> List[Space]:
    return find_({"name": {"like": name}}, Space, SPACES)


def load_space_list_by_user_id_with_pagination(group_ids, pagination: Pagination) -> DataPage:
    return page_({"groupIds": {"in": group_ids}}, [("spaceId", "desc")], pagination, Space, SPACES)


def import_space_to_db(space) -> Space:
    return insert_one(space, Space, SPACES)
