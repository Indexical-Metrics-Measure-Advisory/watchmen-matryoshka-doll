import logging

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.topic.storage.topic_schema_storage import save_topic, update_topic, get_topic
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


def create_topic_schema(topic):
    topic = get_topic(topic.name)
    if topic is not None:
        raise Exception("topic already exist")
    if topic.topicId is None:
        topic.topicId = get_surrogate_key()
    if type(topic) is not dict:
        topic = topic.dict()
    save_topic(topic)
    return topic


def update_topic_schema(
        topic_id,
        topic: Topic):
    if type(topic) is not dict:
        topic = topic.dict()
    update_topic(topic_id, topic)
    return topic
