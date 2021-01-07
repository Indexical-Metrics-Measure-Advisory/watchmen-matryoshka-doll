from bson import regex

from watchmen.common.pagination import Pagination
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils import pickle_wrapper
from watchmen.common.utils.data_utils import WATCHMEN
from watchmen.space.space import Space

db = get_client(WATCHMEN)

collection = db.get_collection('space')


def insert_space_to_storage(space):
    return collection.insert_one(space)


def update_space_to_storage(space_id: int, space: Space):
    return collection.update_one({"spaceId": space_id}, {"$set": space})


def query_space_with_pagination(query_name: str, pagination: Pagination):
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    result = collection.find({"name": regex.Regex(query_name)}).skip(skips).limit(pagination.pageSize)
    return list(result)


def load_space_by_user(user):
    data = collection.find_one({"user": user})
    return pickle_wrapper(data, Space)


def load_space_by_name(name):
    data = collection.find_one({"name": name})
    return pickle_wrapper(data, Space)


def load_space_list_by_user_id_with_pagination(user_id, pagination: Pagination):
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    data_list = collection.find_one({"createUser": user_id}).skip(skips).limit(pagination.pageSize)
    if data_list is None or len(data_list) == 0:
        data_list = collection.find({"accessUsers": {"$in": [user_id]}})
        return pickle_wrapper(data_list, Space)
    else:
        return pickle_wrapper(data_list, Space)
