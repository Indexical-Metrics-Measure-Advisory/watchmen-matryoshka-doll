from watchmen.storage.engine.storage_engine import get_client

db = get_client("watchmen")

collection = db.get_collection('master_space')


def save_master_space(master_space):
    if type(master_space) is not dict:
        master_space = master_space.dict()
    return collection.insert_one(master_space)


def update_master_space(master_space):
    collection.updateOne({"_id": master_space.id})
