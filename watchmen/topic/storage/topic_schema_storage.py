from typing import List

from model.model.common.data_page import DataPage
from model.model.common.pagination import Pagination
from model.model.topic.topic import Topic
from storage.storage.storage_interface import OrderType

from watchmen_boot.cache.cache_manage import cacheman, TOPIC_BY_ID, TOPIC_BY_NAME, COLUMNS_BY_TABLE_NAME, \
    TOPIC_DICT_BY_NAME
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.database.find_storage_template import find_storage_template

TOPICS = "topics"

storage_template = find_storage_template()


def save_topic(topic: Topic) -> Topic:
    return storage_template.insert_one(topic, Topic, TOPICS)


def load_all_topic(current_user) -> List[Topic]:
    # return list_all(Topic, TOPICS)
    return storage_template.find_({"tenantId": current_user.tenantId}, Topic, TOPICS)


def load_all_topic_list(pagination: Pagination, current_user) -> DataPage:
    sort_dict = [{"last_modified": OrderType.DESCENDING}]
    return storage_template.page_({"tenantId": current_user}, sort_dict, pagination, Topic, TOPICS)


def get_topic_by_name(topic_name: str, current_user=None) -> Topic:
    cached_topic = cacheman[TOPIC_BY_NAME].get(topic_name)
    if cached_topic is not None:
        return cached_topic
    if current_user is None:
        result = storage_template.find_one({"name": topic_name}, Topic, TOPICS)
    else:
        result = storage_template.find_one({"and": [{"name": topic_name}, {"tenantId": current_user.tenantId}]}, Topic,
                                           TOPICS)
    cacheman[TOPIC_BY_NAME].set(topic_name, result)
    return result


def get_topic_by_name_and_tenant_id(topic_name: str, tenant_id: str):
    cached_topic = cacheman[TOPIC_BY_NAME].get(topic_name)
    if cached_topic is not None:
        return cached_topic
    if tenant_id is None:
        raise Exception("tenant_id is empty")
    else:
        result = storage_template.find_one({"and": [{"name": topic_name}, {"tenantId": tenant_id}]}, Topic,
                                           TOPICS)
    cacheman[TOPIC_BY_NAME].set(topic_name, result)
    return result


def get_topic(topic_name: str, current_user=None) -> Topic:
    return get_topic_by_name(topic_name, current_user)


def load_topic_list_by_name(topic_name: str, current_user) -> List[Topic]:
    where = {"and": [{"name": {"like": topic_name}}, {"tenantId": current_user.tenantId}], }
    return storage_template.find_(where, Topic, TOPICS)


def load_topic_list_by_name_and_exclude(topic_name, topic_type, current_user) -> List[Topic]:
    where = {
        "and": [{"name": {"like": topic_name}}, {"type": {"!=": topic_type}}, {"tenantId": current_user.tenantId}], }
    return storage_template.find_(where, Topic, TOPICS)


def load_topic_by_name(topic_name: str, current_user) -> Topic:
    cached_topic = cacheman[TOPIC_BY_NAME].get(topic_name)
    if cached_topic is not None:
        return cached_topic
    result = storage_template.find_one({"and": [{"name": topic_name}, {"tenantId": current_user.tenantId}]}, Topic,
                                       TOPICS)
    cacheman[TOPIC_BY_NAME].set(topic_name, result)
    return result


def get_topic_list_all():
    return storage_template.list_all(Topic, TOPICS)


def get_topic_by_id(topic_id: str, current_user=None) -> Topic:
    cached_topic = cacheman[TOPIC_BY_ID].get(topic_id)
    if cached_topic is not None:
        return cached_topic

    if current_user is None:
        result = storage_template.find_one({"topicId": topic_id}, Topic, TOPICS)
        if result is not None:
            cacheman[TOPIC_BY_ID].set(topic_id, result)
        return result

    else:
        result = storage_template.find_one({"and": [{"topicId": topic_id}, {"tenantId": current_user.tenantId}]}, Topic,
                                           TOPICS)
        if result is not None:
            cacheman[TOPIC_BY_ID].set(topic_id, result)
        return result


def get_topic_list_by_ids(topic_ids: List[str], current_user) -> List[Topic]:
    if len(topic_ids) > 0:
        where = {"and": [{"topicId": {"in": topic_ids}}, {"tenantId": current_user.tenantId}]}
        return storage_template.find_(where, Topic, TOPICS)
    else:
        return storage_template.find_({"tenantId": current_user.tenantId}, Topic, TOPICS)


def query_topic_list_with_pagination(query_name: str, pagination: Pagination, current_user) -> DataPage:
    if query_name != '':
        query_dict = {"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]}
        sort_dict = [("lastmodified", "desc")]
        return storage_template.page_(query_dict, sort_dict, pagination, Topic, TOPICS)
    else:
        sort_dict = [("lastmodified", "desc")]
        return storage_template.page_({"tenantId": current_user.tenantId}, sort_dict, pagination, Topic, TOPICS)


def update_topic(topic_id: str, topic: Topic) -> Topic:
    result = storage_template.update_one(topic, Topic, TOPICS)
    cacheman[TOPIC_BY_NAME].delete(topic.name)
    cacheman[TOPIC_DICT_BY_NAME].delete(topic.name)
    cacheman[TOPIC_BY_ID].delete(topic_id)
    cacheman[COLUMNS_BY_TABLE_NAME].delete(build_collection_name(topic.name))
    return result


def import_topic_to_db(topic: Topic) -> Topic:
    result = storage_template.insert_one(topic, Topic, TOPICS)
    cacheman[TOPIC_BY_NAME].delete(topic.name)
    cacheman[TOPIC_DICT_BY_NAME].delete(topic.name)
    cacheman[TOPIC_BY_ID].delete(topic.topicId)
    cacheman[COLUMNS_BY_TABLE_NAME].delete(build_collection_name(topic.name))
    return result
