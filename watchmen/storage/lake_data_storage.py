from watchmen.storage.engine.storage_engine import get_client

db = get_client("watchmen")


def batch_import_data(data_list, name):
    collection = db.get_collection(name)
    return collection.insert_many(data_list)
