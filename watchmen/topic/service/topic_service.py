import logging

from watchmen.topic.storage.topic_schema_storage import save_topic, get_topic_list_like_topic_name, get_topic_by_id
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


def create_topic_schema(topic:Topic):
    if topic is not dict:
        topic = topic.dict()
    insert_topic = save_topic(topic)
    topic["_id"]=insert_topic.inserted_id
    return topic


def update_topic_schema(topic_id,topic:Topic):
    topic = get_topic_by_id(topic_id)
    if topic is not None:
        pass

    pass


def query_topic_schema(query_name:str):
    data_list = get_topic_list_like_topic_name(query_name)
    return list(data_list)








