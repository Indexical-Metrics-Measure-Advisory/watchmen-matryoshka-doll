from functools import lru_cache

import pymongo
from bson import regex

from watchmen.common.pagination import Pagination
from watchmen.common.storage.engine_adaptor import find_template
from watchmen.topic.topic import Topic

# db = get_client()
#
# topics = db.get_collection('topics')

template = find_template()


def save_topic(topic):
    # print(get_topic_by_id.cache_info())
    get_topic_by_id.cache_clear()
    get_topic.cache_clear()
    # return topics.insert_one(topic)
    return template.create("topics", topic, Topic)


def load_all_topic():
    # result = topics.find()
    # # .sort("last_modified", pymongo.DESCENDING)
    # return list(result)
    return template.find_all("topics", Topic)


def load_all_topic_list(pagination: Pagination):
    # item_count = topics.find().count()
    # skips = pagination.pageSize * (pagination.pageNumber - 1)
    # result = topics.find().skip(skips).limit(pagination.pageSize).sort("last_modified", pymongo.DESCENDING)
    # return build_data_pages(pagination, list(result), item_count)
    return template.query_with_pagination("topics", pagination, Topic, sort_dict={"last_modified": pymongo.DESCENDING})


def get_topic_by_name(topic_name):
    # return topics.find_one({"name": topic_name})
    return template.find_one("topics", {"name": topic_name}, Topic)


@lru_cache(maxsize=50)
def get_topic(topic_name) -> Topic:
    # result = topics.find_one({"name": topic_name})
    # if result is None:
    #     pass
    # else:
    #     return Topic.parse_obj(result)
    return template.find_one("topics", {"name": topic_name}, Topic)


def load_topic_list_by_name(topic_name):
    # result = topics.find({"name": regex.Regex(topic_name)})
    # return list(result)
    return template.find("topics", {"name": regex.Regex(topic_name)}, Topic)


def check_topic_exist(topic_name, topic_type) -> bool:
    # result = topics.find_one({"name", topic_name, "type", topic_type})
    result = template.find_one("topics", {"name", topic_name, "type", topic_type}, Topic)
    if result is None:
        return False
    else:
        return True


@lru_cache(maxsize=50)
def get_topic_by_id(topic_id):
    # result = topics.find_one({"topicId": topic_id})
    # if result is None:
    #     return
    # else:
    #     return Topic.parse_obj(result)
    return template.find_one("topics", {"topicId": topic_id}, Topic)


def get_topic_list_by_ids(topic_ids):
    # result = topics.find({"topicId": {"$in": topic_ids}})
    # return list(result)
    return template.find("topics", {"topicId": {"$in": topic_ids}}, Topic)


def query_topic_list_with_pagination(query_name: str, pagination: Pagination):
    # item_count = topics.find({"name": regex.Regex(query_name)}).count()
    # skips = pagination.pageSize * (pagination.pageNumber - 1)
    # result = topics.find({"name": regex.Regex(query_name)}).skip(skips).limit(pagination.pageSize).sort(
    #     "last_modified", pymongo.DESCENDING)
    # return build_data_pages(pagination, list(result), item_count)
    return template.query_with_pagination("topics", pagination, Topic, query_dict={"name": regex.Regex(query_name)},
                                          sort_dict=["last_modified", pymongo.DESCENDING])


def update_topic(topic_id, topic: Topic):
    # get_topic_by_id.cache_clear()
    # get_topic.cache_clear()
    # return topics.update_one({"topicId": topic_id}, {"$set": topic})

    return template.update_one("topics", {"topicId": topic_id}, topic, Topic)


def import_topic_to_db(topic):
    return template.create("topics", topic, Topic)
    # topics.insert_one(topic.dict())
