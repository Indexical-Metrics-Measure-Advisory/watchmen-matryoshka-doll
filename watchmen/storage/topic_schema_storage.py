from watchmen.space.factors.topic import Topic
from watchmen.storage.engine.storage_engine import get_client


from watchmen.utils.data_utils import WATCHMEN

db = get_client(WATCHMEN)

topic_col = db.get_collection('topic')


def save_topic(topic):
    return topic_col.insert_one(topic)


def get_topic_by_name(topic_name):
    return topic_col.find_one("topicName", topic_name)


def get_topic_by_id(topic_id):
    return topic_col.find_one("_id", topic_id)


def get_topic_list_by_ids(topic_ids):
    # print(topic_ids)
    return topic_col.find({"_id": {"$in": topic_ids}})


def topic_dict_to_object(topic_schema_dict):
    topic =Topic()
    return topic


