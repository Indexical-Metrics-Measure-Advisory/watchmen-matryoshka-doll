from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name

db = get_client()


# TODO operator for mongo
def __build_mongo_condition(where_condition, mode):
    result = {}
    if len(where_condition) > 1:
        for condition in where_condition:
            if condition["operator"] == "equals":
                name = condition["name"]
                value = condition["value"]
                result[name] = value
        return result
    else:
        condition = where_condition[0]
        if condition["operator"] == "equals":
            return {condition["name"]: condition["value"]}


def read_topic_data(where_condition, topic_name, mode):
    collection_name = build_collection_name(topic_name)
    collection = db.get_collection(collection_name)
    condition = __build_mongo_condition(where_condition, mode)
    result = collection.find_one(condition)
    return result
