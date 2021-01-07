from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN

db = get_client(WATCHMEN)
collection = db.get_collection('raw_schema')


def insert_data_schema(data):
    return collection.insert_one(data)


def update_data_schema(id, data):
    return collection.update_one({"id": id}, {"$set": data})


def load_raw_schema_by_code(code):
    return collection.find_one({"code": code})


def delete_data_schema_by_id(id):
    return collection.delete_one({"_id": id})
