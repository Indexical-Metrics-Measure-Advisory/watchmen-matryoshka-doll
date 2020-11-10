

from watchmen.storage.engine.storage_engine import get_client
from watchmen.factors.model.topic import Topic

import datetime

from watchmen.utils.data_utils import WATCHMEN

db = get_client(WATCHMEN)

topic_col = db.get_collection('topic')

def save_topic(topic):
    return topic_col.insert_one(topic)

def get_topic_by_name(topicName):
    return topic_col.find_one("topicName", topicName)

def get_topic_by_id(topicId):
    return topic_col.find_one("topicId", topicId)

def get_topic_by_ids(topicIds):
    return topic_col.find({"topicId", {"$in": topicIds}})

def topic_dict_to_object(topic_schema_dict):
    topic =Topic()
    return topic


