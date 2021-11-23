from typing import List

from watchmen.common.data_page import DataPage
from watchmen.common.model.user import User
from watchmen.common.pagination import Pagination
from watchmen.database.find_storage_template import find_storage_template
from watchmen.space.space import Space, SpaceFilter

SPACES = "spaces"

storage_template = find_storage_template()


def insert_space_to_storage(space) -> Space:
    return storage_template.insert_one(space, Space, SPACES)


def get_space_by_id(space_id: str, current_user: User) -> Space:
    return storage_template.find_one({"and": [{"spaceId": space_id}, {"tenantId": current_user.tenantId}]}, Space, SPACES)


def update_space_to_storage(space_id: str, space: Space) -> Space:
    return storage_template.update_one(space, Space, SPACES)


def query_space_with_pagination(query_name: str, pagination: Pagination, current_user) -> DataPage:
    return storage_template.page_({"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]}, [("name", "desc")],
                 pagination, Space, SPACES)


def get_space_list_by_ids(space_ids, current_user) -> List[Space]:
    if space_ids:
        return storage_template.find_({"and": [{"spaceId": {"in": space_ids}}, {"tenantId": current_user.tenantId}]}, Space, SPACES)
    else:
        return []


def get_filters_by_id(space_id, current_user) -> List[SpaceFilter]:
    space: Space = storage_template.find_one({"and": [{"spaceId": space_id}, {"tenantId": current_user.tenantId}]}, Space, SPACES)
    return space.filters


## TODO  in for and
def load_space_by_user(group_ids, current_user) -> List[Space]:
    if group_ids:
        # return find_({"and":[{"groupIds": {"in": group_ids}},{"tenantId":current_user.tenantId}]}, Space, SPACES)
        return storage_template.find_({"groupIds": {"in": group_ids}}, Space, SPACES)
    else:
        return []


def load_space_by_name(name, current_user) -> Space:
    return storage_template.find_one({"and": [{"name": name}, {"tenantId": current_user.tenantId}]}, Space, SPACES)


def load_space_list_by_name(name, current_user) -> List[Space]:
    return storage_template.find_({"and": [{"name": {"like": name}}, {"tenantId": current_user.tenantId}]}, Space, SPACES)


def load_space_list_by_user_id_with_pagination(group_ids, pagination: Pagination, current_user) -> DataPage:
    return storage_template.page_({"and": [{"groupIds": {"in": group_ids}}, {"tenantId": current_user.tenantId}]}, [("spaceId", "desc")],
                 pagination, Space, SPACES)


def import_space_to_db(space) -> Space:
    return storage_template.insert_one(space, Space, SPACES)
