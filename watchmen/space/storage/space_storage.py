from watchmen.common.pagination import Pagination
from watchmen.space.space import Space
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN
from watchmen.common.utils import pickle_wrapper

db = get_client(WATCHMEN)

collection = db.get_collection('space')


def insert_space_to_storage(space):
    if type(space) is not dict:
        space = space.dict()
    return collection.insert_one(space)


def update_space_to_storage(space:Space):
    if type(space) is not dict:
        space = space.dict()
    query = {"name": space["name"]}
    new_values = {"$set": {"topic_list": space["topic_list"]}}
    collection.update_one(query,new_values)


def load_space_by_user(user):
    data = collection.find_one({"user": user})
    print(data)
    return pickle_wrapper(data, Space)


def load_space_by_name(name):
    data = collection.find_one({"name": name})
    return pickle_wrapper(data, Space)


def load_space_list_by_user_id_with_pagination(user_id, pagination: Pagination):
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    data_list = collection.find_one({"createUser": user_id}).skip(skips).limit(pagination.pageSize)
    if data_list is None or len(data_list) ==0:
        data_list = collection.find({"accessUsers": {"$in": [user_id]}})
        return pickle_wrapper(data_list, Space)
    else:
        return pickle_wrapper(data_list, Space)


