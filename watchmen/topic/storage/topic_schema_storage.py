from functools import lru_cache
from typing import List

from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.common.storage.storage_template import insert_one, list_all, update_one, page_all, OrderType, find_one, \
    exists, page_, find_, find_by_id
from watchmen.topic.topic import Topic

TOPICS = "topics"


# template = find_template()
# template = mysql_template


def save_topic(topic: Topic) -> Topic:
    get_topic_by_id.cache_clear()
    get_topic.cache_clear()
    # return template.create(TOPICS, topic, Topic)
    return insert_one(topic, Topic, TOPICS)


def load_all_topic() -> List[Topic]:
    # return template.find_all(TOPICS, Topic)
    return list_all(Topic, TOPICS)


def load_all_topic_list(pagination: Pagination) -> DataPage:
    # return template.query_with_pagination(TOPICS, pagination, Topic, sort_dict={"last_modified": pymongo.DESCENDING})
    sort_dict = [{"last_modified": OrderType.DESCENDING}]
    return page_all(sort_dict, pagination, Topic, TOPICS)


def get_topic_by_name(topic_name: str) -> Topic:
    # return template.find_one(TOPICS, {"name": topic_name}, Topic)
    return find_one({"name": topic_name}, Topic, TOPICS)


@lru_cache(maxsize=50)
def get_topic(topic_name: str) -> Topic:
    # return template.find_one(TOPICS, {"name": topic_name}, Topic)
    return find_one({"name": topic_name}, Topic, TOPICS)


def load_topic_list_by_name(topic_name: str) -> List[Topic]:
    # return template.find(TOPICS, {"name": regex.Regex(topic_name)}, Topic)
    where = {"name": {"like": topic_name}}
    return find_(where, Topic, TOPICS)


def load_topic_by_name(topic_name: str) -> Topic:
    # return template.find_one(TOPICS, {"name": topic_name}, Topic)
    return find_one({"name": topic_name}, Topic, TOPICS)


def check_topic_exist(topic_name: str, topic_type: str) -> bool:
    '''
    result = template.find_one(
        TOPICS, {"name", topic_name, "type", topic_type}, Topic)
    if result is None:
        return False
    else:
        return True
    '''
    where = {"name", topic_name, "type", topic_type}
    return exists(where, Topic, topic_name)


@lru_cache(maxsize=50)
def get_topic_by_id(topic_id: str) -> Topic:
    # return template.find_one(TOPICS, {"topicId": topic_id}, Topic)
    return find_by_id(topic_id, Topic, TOPICS)


def get_topic_list_by_ids(topic_ids: List[str]) -> List[Topic]:
    # return template.find(TOPICS, {"topicId": {"$in": topic_ids}}, Topic)
    print(topic_ids)
    where = {"topicId": {"in": topic_ids}}
    return find_(where, Topic, TOPICS)


def query_topic_list_with_pagination(query_name: str, pagination: Pagination) -> DataPage:
    '''
    return template.query_with_pagination(TOPICS, pagination, Topic, query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])
    '''
    # query_dict = {"name": regex.Regex(query_name)}
    # sort_dict = [{"last_modified": pymongo.DESCENDING}]
    query_dict = {"name": {"like": query_name}}
    sort_dict = [("last_modified", "desc")]
    return page_(query_dict, sort_dict, pagination, Topic, TOPICS)


def update_topic(topic_id: str, topic: Topic) -> Topic:
    get_topic_by_id.cache_clear()
    get_topic.cache_clear()
    return update_one(topic, Topic, TOPICS)


def import_topic_to_db(topic: Topic) -> Topic:
    get_topic_by_id.cache_clear()
    get_topic.cache_clear()
    # return template.create(TOPICS, topic, Topic)
    return insert_one(topic, Topic, TOPICS)
