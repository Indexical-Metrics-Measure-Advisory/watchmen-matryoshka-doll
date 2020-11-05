
from watchmen.master.master_schema import MasterSchema
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
    return pickle_wrapper(data,MasterSchema)
