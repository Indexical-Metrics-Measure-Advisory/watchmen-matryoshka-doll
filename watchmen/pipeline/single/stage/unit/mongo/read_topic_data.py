from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name

db = get_client()


def query_topic_data(mongo_query, topic_name):
    collection_name = build_collection_name(topic_name)
    collection = db.get_collection(collection_name)
    result = collection.find_one(mongo_query)
    return result
