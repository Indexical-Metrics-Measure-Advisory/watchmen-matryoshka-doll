from functools import lru_cache
from typing import List

import pymongo
from bson import regex

from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.topic.topic import Topic

TOPICS = "topics"

template = find_template()


def save_topic(topic:Topic) -> Topic:
    get_topic_by_id.cache_clear()
    get_topic.cache_clear()
    return template.create(TOPICS, topic, Topic)


def load_all_topic() -> List[Topic]:
    return template.find_all(TOPICS, Topic)


def load_all_topic_list(pagination: Pagination) -> DataPage:
    return template.query_with_pagination(TOPICS, pagination, Topic, sort_dict={"last_modified": pymongo.DESCENDING})


def get_topic_by_name(topic_name:str) -> Topic:
    return template.find_one(TOPICS, {"name": topic_name}, Topic)


@lru_cache(maxsize=50)
def get_topic(topic_name:str) -> Topic:
    return template.find_one(TOPICS, {"name": topic_name}, Topic)


def load_topic_list_by_name(topic_name:str) -> List[Topic]:
    return template.find(TOPICS, {"name": regex.Regex(topic_name)}, Topic)


def check_topic_exist(topic_name:str, topic_type:str) -> bool:
    result = template.find_one(TOPICS, {"name", topic_name, "type", topic_type}, Topic)
    if result is None:
        return False
    else:
        return True


@lru_cache(maxsize=50)
def get_topic_by_id(topic_id:str) -> Topic:
    return template.find_one(TOPICS, {"topicId": topic_id}, Topic)


def get_topic_list_by_ids(topic_ids:List[str]) -> List[Topic]:
    return template.find(TOPICS, {"topicId": {"$in": topic_ids}}, Topic)


def query_topic_list_with_pagination(query_name: str, pagination: Pagination) -> DataPage:
    return template.query_with_pagination(TOPICS, pagination, Topic, query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])


def update_topic(topic_id:str, topic: Topic) -> Topic:
    get_topic_by_id.cache_clear()
    get_topic.cache_clear()
    return template.update_one(TOPICS, {"topicId": topic_id}, topic, Topic)


def import_topic_to_db(topic:Topic) -> Topic:
    get_topic_by_id.cache_clear()
    get_topic.cache_clear()
    return template.create(TOPICS, topic, Topic)
