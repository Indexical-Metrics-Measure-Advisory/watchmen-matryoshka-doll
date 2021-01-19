from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN, build_collection_name

db = get_client(WATCHMEN)


def __build_mongo_condition(where_condition, mode):
    if len(where_condition) > 1:
        # TODO multiple conditions
        pass
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
