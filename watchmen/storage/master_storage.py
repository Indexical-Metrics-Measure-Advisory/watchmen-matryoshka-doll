from watchmen.entity.pagination import Pagination
from watchmen.master.master_space import MasterSpace
from watchmen.storage.engine.storage_engine import get_client
from watchmen.utils.data_utils import WATCHMEN
from watchmen.utils.pickle_wrapper import pickle_wrapper

db = get_client(WATCHMEN)

collection = db.get_collection('master_space')


def save_master_space(master_space):
    if type(master_space) is not dict:
        master_space = master_space.dict()
    return collection.insert_one(master_space)


def update_master_space(master_space):
    collection.updateOne({"_id": master_space.id})


def load_master_space_by_user(user):
    data = collection.find_one({"user": user})
    print(data)
    return pickle_wrapper(data, MasterSpace)


def load_master_space_by_name(name):
    data = collection.find_one({"name": name})
    return pickle_wrapper(data, MasterSpace)


def load_space_list_by_user_id_with_pagination(user_id, pagination: Pagination):
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    data = collection.find_one({"user": user_id}).skip(skips).limit(pagination.pageSize)
    return pickle_wrapper(data, MasterSpace)
