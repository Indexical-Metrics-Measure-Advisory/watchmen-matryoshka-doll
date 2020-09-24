from watchmen.storage.engine.storage_engine import get_client

db = get_client("watchmen")

collection = db.get_collection('factors')


def save_factor(factor):
    return collection.insert_one(factor)


def load_factor_id(factor_id):
    return collection.find_one(factor_id)


def load_factors_by_topic_id(topic_id):
    pass

