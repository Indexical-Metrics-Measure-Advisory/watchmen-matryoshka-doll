from bson import regex

from watchmen.common.pagination import Pagination
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils import pickle_wrapper
from watchmen.common.utils.data_utils import WATCHMEN, build_data_pages
from watchmen.space.space import Space

db = get_client(WATCHMEN)

collection = db.get_collection('space')


def insert_space_to_storage(space):
    return collection.insert_one(space)


def get_space_by_id(space_id: str):
    result =  collection.find_one({"spaceId": space_id})
    return Space.parse_obj(result)


def update_space_to_storage(space_id: str, space: Space):
    return collection.update_one({"spaceId": space_id}, {"$set": space})


def query_space_with_pagination(query_name: str, pagination: Pagination):
    items_count = collection.find({"name": regex.Regex(query_name)}).count()
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    result = collection.find({"name": regex.Regex(query_name)}).skip(skips).limit(pagination.pageSize)
    return build_data_pages(pagination, list(result), items_count)


def get_space_list_by_ids(space_ids):
    result = collection.find({"spaceId": {"$in": space_ids}})
    return list(result)


def load_space_by_user(group_ids):
    result = collection.find({"groupIds": {"$in": group_ids}})
    return list(result)


def load_space_by_name(name):
    data = collection.find_one({"name": name})
    return data


def load_space_list_by_name(name):
    result = collection.find({"name": regex.Regex(name)})
    return list(result)


def load_space_list_by_user_id_with_pagination(group_ids, pagination: Pagination):
    items_count = collection.find({"groupIds": {"$in": group_ids}}).count()
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    result = collection.find({"groupIds": {"$in": group_ids}}).skip(skips).limit(pagination.pageSize)
    return build_data_pages(pagination, list(result), items_count)


