from typing import List

from cacheout import Cache

from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.config.config import settings, PROD
from watchmen.database.storage.storage_interface import OrderType
from watchmen.database.storage.storage_template import insert_one, update_one, find_one, \
    page_, find_
from watchmen.topic.topic import Topic

TOPICS = "topics"

cache = Cache()


def save_topic(topic: Topic) -> Topic:
    return insert_one(topic, Topic, TOPICS)


def load_all_topic(current_user) -> List[Topic]:
    # return list_all(Topic, TOPICS)
    return find_({"tenantId": current_user.tenantId}, Topic, TOPICS)


def load_all_topic_list(pagination: Pagination, current_user) -> DataPage:
    # return template.query_with_pagination(TOPICS, pagination, Topic, sort_dict={"last_modified": pymongo.DESCENDING})
    sort_dict = [{"last_modified": OrderType.DESCENDING}]
    return page_({"tenantId": current_user}, sort_dict, pagination, Topic, TOPICS)


def get_topic_by_name(topic_name: str, current_user) -> Topic:
    # return template.find_one(TOPICS, {"name": topic_name}, Topic)
    return find_one({"and": [{"name": topic_name}, {"tenantId": current_user.tenantId}]}, Topic, TOPICS)


def get_topic(topic_name: str, current_user=None) -> Topic:
    if current_user is None:
        return find_one({"name": topic_name}, Topic, TOPICS)
    else:
        return find_one({"and": [{"name": topic_name}, {"tenantId": current_user.tenantId}]}, Topic, TOPICS)


def load_topic_list_by_name(topic_name: str, current_user) -> List[Topic]:
    where = {"and": [{"name": {"like": topic_name}}, {"tenantId": current_user.tenantId}], }
    return find_(where, Topic, TOPICS)


def load_topic_by_name(topic_name: str, current_user) -> Topic:
    return find_one({"and": [{"name": topic_name}, {"tenantId": current_user.tenantId}]}, Topic, TOPICS)


def get_topic_by_id(topic_id: str, current_user=None) -> Topic:
    if topic_id in cache and settings.ENVIRONMENT == PROD:
        return cache.get(topic_id)
    if current_user is None:
        result = find_one({"topicId": topic_id}, Topic, TOPICS)
        cache.set(topic_id, result)
        return result
    else:
        result = find_one({"and": [{"topicId": topic_id}, {"tenantId": current_user.tenantId}]}, Topic, TOPICS)
        cache.set(topic_id, result)
        return result



def get_topic_list_by_ids(topic_ids: List[str], current_user) -> List[Topic]:
    if len(topic_ids) > 0:
        where = {"and": [{"topicId": {"in": topic_ids}}, {"tenantId": current_user.tenantId}], }
        return find_(where, Topic, TOPICS)
    else:
        return find_({"tenantId": current_user.tenantId}, Topic, TOPICS)


def query_topic_list_with_pagination(query_name: str, pagination: Pagination, current_user) -> DataPage:
    '''
    return template.query_with_pagination(TOPICS, pagination, Topic, query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])
    '''

    if query_name != '':
        query_dict = {"and": [{"name": {"like": query_name}}, {"tenantId": current_user.tenantId}]}
        sort_dict = [("lastmodified", "desc")]
        return page_(query_dict, sort_dict, pagination, Topic, TOPICS)
    else:
        sort_dict = [("lastmodified", "desc")]
        return page_({"tenantId": current_user.tenantId}, sort_dict, pagination, Topic, TOPICS)


def update_topic(topic_id: str, topic: Topic) -> Topic:
    # get_topic_by_id.cache_clear()
    # get_topic.cache_clear()
    return update_one(topic, Topic, TOPICS)


def import_topic_to_db(topic: Topic) -> Topic:
    # get_topic_by_id.cache_clear()
    # get_topic.cache_clear()
    return insert_one(topic, Topic, TOPICS)
