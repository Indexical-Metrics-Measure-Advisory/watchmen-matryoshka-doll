from typing import List

from watchmen.common.cache.cache_manage import cacheman, TOPIC_BY_ID, TOPIC_BY_NAME, COLUMNS_BY_TABLE_NAME, \
    TOPIC_DICT_BY_NAME
from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.database.storage.storage_interface import OrderType
from watchmen.database.storage.storage_template import insert_one, update_one, find_one, \
    page_, find_
from watchmen.topic.topic import Topic

TOPICS = "topics"


def save_topic(topic: Topic) -> Topic:
    return insert_one(topic, Topic, TOPICS)


def load_all_topic(current_user) -> List[Topic]:
    # return list_all(Topic, TOPICS)
    return find_({"tenantId": current_user.tenantId}, Topic, TOPICS)


def load_all_topic_list(pagination: Pagination, current_user) -> DataPage:
    sort_dict = [{"last_modified": OrderType.DESCENDING}]
    return page_({"tenantId": current_user}, sort_dict, pagination, Topic, TOPICS)


def get_topic_by_name(topic_name: str, current_user=None) -> Topic:
    cached_topic = cacheman[TOPIC_BY_NAME].get(topic_name)
    if cached_topic is not None:
        return cached_topic
    if current_user is None:
        result = find_one({"name": topic_name}, Topic, TOPICS)
    else:
        result = find_one({"and": [{"name": topic_name}, {"tenantId": current_user.tenantId}]}, Topic, TOPICS)
    cacheman[TOPIC_BY_NAME].set(topic_name, result)
    return result


def get_topic(topic_name: str, current_user=None) -> Topic:
    return get_topic_by_name(topic_name, current_user)


def load_topic_list_by_name(topic_name: str, current_user) -> List[Topic]:
    where = {"and": [{"name": {"like": topic_name}}, {"tenantId": current_user.tenantId}], }
    return find_(where, Topic, TOPICS)


def load_topic_by_name(topic_name: str, current_user) -> Topic:
    cached_topic = cacheman[TOPIC_BY_NAME].get(topic_name)
    if cached_topic is not None:
        return cached_topic
    result = find_one({"and": [{"name": topic_name}, {"tenantId": current_user.tenantId}]}, Topic, TOPICS)
    cacheman[TOPIC_BY_NAME].set(topic_name, result)
    return result


def get_topic_by_id(topic_id: str, current_user=None) -> Topic:
    cached_topic = cacheman[TOPIC_BY_ID].get(topic_id)
    if cached_topic is not None:
        return cached_topic

    if current_user is None:
        result = find_one({"topicId": topic_id}, Topic, TOPICS)
        if result is not None:
            cacheman[TOPIC_BY_ID].set(topic_id, result)
        return result

    else:
        result = find_one({"and": [{"topicId": topic_id}, {"tenantId": current_user.tenantId}]}, Topic, TOPICS)
        if result is not None:
            cacheman[TOPIC_BY_ID].set(topic_id, result)
        return result


def get_topic_list_by_ids(topic_ids: List[str], current_user) -> List[Topic]:
    if len(topic_ids) > 0:
        where = {"and": [{"topicId": {"in": topic_ids}}, {"tenantId": current_user.tenantId}], }
        return find_(where, Topic, TOPICS)
    else:
        return find_({"tenantId": current_user.tenantId}, Topic, TOPICS)


def query_topic_list_with_pagination(query_name: str, pagination: Pagination, current_user) -> DataPage:
    if query_name != '':
        query_dict = {"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]}
        sort_dict = [("lastmodified", "desc")]
        return page_(query_dict, sort_dict, pagination, Topic, TOPICS)
    else:
        sort_dict = [("lastmodified", "desc")]
        return page_({"tenantId": current_user.tenantId}, sort_dict, pagination, Topic, TOPICS)


def update_topic(topic_id: str, topic: Topic) -> Topic:
    result = update_one(topic, Topic, TOPICS)
    cacheman[TOPIC_BY_NAME].delete(topic.name)
    cacheman[TOPIC_DICT_BY_NAME].delete(topic.name)
    cacheman[TOPIC_BY_ID].delete(topic_id)
    cacheman[COLUMNS_BY_TABLE_NAME].delete(build_collection_name(topic.name))
    return result


def import_topic_to_db(topic: Topic) -> Topic:
    result = insert_one(topic, Topic, TOPICS)
    cacheman[TOPIC_BY_NAME].delete(topic.name)
    cacheman[TOPIC_DICT_BY_NAME].delete(topic.name)
    cacheman[TOPIC_BY_ID].delete(topic.topicId)
    cacheman[COLUMNS_BY_TABLE_NAME].delete(build_collection_name(topic.name))
    return result
