from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.pipeline.single.stage.unit.mongo.index import build_mongo_condition

db = get_client()


def read_topic_data(where_condition, topic_name, joint_type):
    collection_name = build_collection_name(topic_name)
    collection = db.get_collection(collection_name)
    condition = build_mongo_condition(where_condition, joint_type)
    result = collection.find_one(condition)
    return result
