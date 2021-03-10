from bson import regex

from watchmen.common.pagination import Pagination
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_data_pages
from watchmen.space.space import Space

db = get_client()

spaces = db.get_collection('spaces')


def insert_space_to_storage(space):
    return spaces.insert_one(space)


def get_space_by_id(space_id: str):
    result = spaces.find_one({"spaceId": space_id})
    if result is None:
        return None
    else:
        return Space.parse_obj(result)


def update_space_to_storage(space_id: str, space: Space):
    return spaces.update_one({"spaceId": space_id}, {"$set": space})


def query_space_with_pagination(query_name: str, pagination: Pagination):
    items_count = spaces.find({"name": regex.Regex(query_name)}).count()
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    result = spaces.find({"name": regex.Regex(query_name)}).skip(skips).limit(pagination.pageSize)
    return build_data_pages(pagination, list(result), items_count)


def get_space_list_by_ids(space_ids):
    result = spaces.find({"spaceId": {"$in": space_ids}})
    return list(result)


def load_space_by_user(group_ids):
    result = spaces.find({"groupIds": {"$in": group_ids}})
    return list(result)


def load_space_by_name(name):
    data = spaces.find_one({"name": name})
    return data


def load_space_list_by_name(name):
    result = spaces.find({"name": regex.Regex(name)})
    return list(result)


def load_space_list_by_user_id_with_pagination(group_ids, pagination: Pagination):
    items_count = spaces.find({"groupIds": {"$in": group_ids}}).count()
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    result = spaces.find({"groupIds": {"$in": group_ids}}).skip(skips).limit(pagination.pageSize)
    return build_data_pages(pagination, list(result), items_count)


def import_space_to_db(space):
    spaces.insert_one(space.dict())
