import logging

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.topic.storage.topic_schema_storage import save_topic, update_topic
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


# def __build_factor_id(factor_list):
#     for factor in factor_list:
#         factor["factorId"] = get_surrogate_key()
#     return factor_list


def create_topic_schema(topic):
    # TODO add check topic check
    if type(topic) is not dict:
        topic = topic.dict()
    # topic["factors"]=__build_factor_id(topic["factors"])
    topic["topicId"] = get_surrogate_key()
    save_topic(topic)
    return topic


def update_topic_schema(
        topic_id,
        topic: Topic):
    if type(topic) is not dict:
        topic = topic.dict()
    update_topic(topic_id, topic)
    return topic

#
# def query_topic_schema(query_name:str):
#     data_list = get_topic_list_like_topic_name(query_name)
#     return json_util.dumps(data_list)
