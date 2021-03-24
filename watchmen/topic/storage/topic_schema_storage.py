from functools import lru_cache

import pymongo
from bson import regex

from watchmen.common.mysql import mysql_template
from watchmen.common.pagination import Pagination
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.topic.topic import Topic

TOPICS = "topics"

template = find_template()
#template = mysql_template


def save_topic(topic):
    get_topic_by_id.cache_clear()
    get_topic.cache_clear()
    return template.create(TOPICS, topic, Topic)


def load_all_topic():
    return template.find_all(TOPICS, Topic)


def load_all_topic_list(pagination: Pagination):
    return template.query_with_pagination(TOPICS, pagination, Topic, sort_dict={"last_modified": pymongo.DESCENDING})


def get_topic_by_name(topic_name):
    return template.find_one(TOPICS, {"name": topic_name}, Topic)


@lru_cache(maxsize=50)
def get_topic(topic_name) -> Topic:
    return template.find_one(TOPICS, {"name": topic_name}, Topic)


def load_topic_list_by_name(topic_name):
    return template.find(TOPICS, {"name": regex.Regex(topic_name)}, Topic)


def check_topic_exist(topic_name, topic_type) -> bool:
    result = template.find_one(TOPICS, {"name", topic_name, "type", topic_type}, Topic)
    if result is None:
        return False
    else:
        return True


@lru_cache(maxsize=50)
def get_topic_by_id(topic_id):
    return template.find_one(TOPICS, {"topicId": topic_id}, Topic)


def get_topic_list_by_ids(topic_ids):
    return template.find(TOPICS, {"topicId": {"$in": topic_ids}}, Topic)


def query_topic_list_with_pagination(query_name: str, pagination: Pagination):
    return template.query_with_pagination(TOPICS, pagination, Topic, query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])


def update_topic(topic_id, topic: Topic):
    get_topic_by_id.cache_clear()
    get_topic.cache_clear()
    return template.update_one(TOPICS, {"topicId": topic_id}, topic, Topic)


def import_topic_to_db(topic):
    get_topic_by_id.cache_clear()
    get_topic.cache_clear()
    return template.create(TOPICS, topic, Topic)
