from bson import regex

from watchmen.common.pagination import Pagination
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN, build_data_pages
from watchmen.topic.topic import Topic

db = get_client(WATCHMEN)

topic_col = db.get_collection('topic')


def save_topic(topic):
    return topic_col.insert_one(topic)


def load_all_topic_list(pagination: Pagination):
    item_count = topic_col.find().count()
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    result = topic_col.find().skip(skips).limit(pagination.pageSize)
    return build_data_pages(pagination, list(result), item_count)


def get_topic_by_name(topic_name):
    return topic_col.find_one("code", topic_name)


def get_raw_topic(topic_name)->Topic:
    result = topic_col.find_one({"code": topic_name,"type": "raw"})
    return  Topic.parse_obj(result)


def load_topic_list_by_name(topic_name):
    result = topic_col.find({"code": regex.Regex(topic_name)})
    return list(result)


def check_topic_exist(topic_name, topic_type) -> bool:
    result = topic_col.find_one({"code", topic_name, "type", topic_type})
    if result is None:
        return False
    else:
        return True


# TODO topic cache
def get_topic_by_id(topic_id):
    result =  topic_col.find_one({"topicId": topic_id})
    return Topic.parse_obj(result)


def get_topic_list_by_ids(topic_ids):
    result = topic_col.find({"topicId": {"$in": topic_ids}})
    return list(result)


def topic_dict_to_object(topic_schema_dict):
    topic = Topic()
    return topic


def query_topic_list_with_pagination(query_name: str, pagination: Pagination):
    item_count = topic_col.find({"name": regex.Regex(query_name)}).count()
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    result = topic_col.find({"name": regex.Regex(query_name)}).skip(skips).limit(pagination.pageSize)
    return build_data_pages(pagination, list(result), item_count)


def update_topic(topic_id, topic: Topic):
    return topic_col.update_one({"topicId": topic_id}, {"$set": topic})
