import logging
from datetime import date

import arrow
import pymongo
from bson import regex, ObjectId
from pymongo import ReturnDocument

from watchmen.common.data_page import DataPage
from watchmen.database.mongo.index import build_code_options, get_client
from watchmen.database.storage.utils.table_utils import get_primary_key
from watchmen.common.utils.data_utils import build_data_pages, build_collection_name

client = get_client()

log = logging.getLogger("app." + __name__)

log.info("mongo template initialized")


def build_mongo_where_expression(where: dict):
    """
    Build where, the common sql pattern is "column_name operator value", but we use dict,
    so the pattern is {column_name: {operator: value}}.

    if operator is =, then can use {column_name: value}

    About and|or , use
        {"and": List(
                                {column_name1: {operator: value}}
                                {column_name2: {operator: value}}
                    )
        }

    support Nested:
        {"or": List(
                                {column_name1: {operator: value}}
                                {column_name2: {operator: value}}
                                {"and": List(
                                                        {column_name3:{operator: value}}
                                                        {column_name4:{operator: value}}
                                            )
                                }
                    )
        }
    """
    for key, value in where.items():
        if key == "and" or key == "or":
            if isinstance(value, list):
                filters = []
                for express in value:
                    result = build_mongo_where_expression(express)
                    filters.append(result)
            if key == "and":
                return {"$and": filters}
            if key == "or":
                return {"$or": filters}
        else:
            if isinstance(value, dict):
                for k, v in value.items():
                    if k == "=":
                        return {key: {"$eq": v}}
                    if k == "!=":
                        return {key: {"$ne": v}}
                    if k == "like":
                        return {key: regex.Regex(v)}
                    if k == "in":
                        return {key: {"$in": v}}
                    if k == ">":
                        return {key: {"$gt": v}}
                    if k == ">=":
                        return {key: {"$gte": v}}
                    if k == "<":
                        return {key: {"$lt": v}}
                    if k == "<=":
                        return {key: {"$lte": v}}
                    if k == "between":
                        if (isinstance(v, tuple)) and len(v) == 2:
                            return {key: {"$gte": v[0], "$lt": v[1]}}
            else:
                return {key: {"$eq": value}}


def build_mongo_update_expression(updates):
    """
    # used in pull_update, just allowed to update one field
    """
    for key, value in updates.items():
        if isinstance(value, dict):
            for k, v in value.items():
                if k == "in":
                    return {key: {"$in": v}}


def build_mongo_updates_expression_for_insert(updates):
    new_updates = {}
    for key, value in updates.items():
        if key == "$inc":
            pass
        elif key == "$set":
            pass
        if isinstance(value, dict):
            for k, v in value.items():
                if k == "_sum":
                    new_updates[key] = v
                elif k == "_count":
                    new_updates[key] = v
        else:
            new_updates[key] = value
    return new_updates


def build_mongo_updates_expression_for_update(updates):
    new_updates = {}
    new_updates["$set"] = {}
    print("updates", updates)
    for key, value in updates.items():
        if isinstance(value, dict):
            for k, v in value.items():
                if k == "_sum":
                    new_updates['$inc'] = {key: v}
                elif k == "_count":
                    new_updates['$inc'][key] = v
        else:
            new_updates["$set"][key]=value
    return new_updates


def build_mongo_order(order_: list):
    result = []
    for item in order_:
        if isinstance(item, tuple):
            if item[1] == "desc":
                new_ = (item[0], pymongo.DESCENDING)
                result.append(new_)
            if item[1] == "asc":
                new_ = (item[0], pymongo.ASCENDING)
                result.append(new_)
    return result


def insert_one(one, model, name):
    collection = client.get_collection(name)
    collection.insert_one(__convert_to_dict(one))
    return model.parse_obj(one)


def insert_all(data, model, name):
    collection = client.get_collection(name)
    collection.insert_many(__convert_list_to_dict(data))
    return data


def update_one(one, model, name) -> any:
    collection = client.get_collection(name)
    primary_key = get_primary_key(name)
    one_dict = __convert_to_dict(one)
    query_dict = {primary_key: one_dict.get(primary_key)}
    collection.update_one(query_dict, {"$set": one_dict})
    return model.parse_obj(one)


def update_one_first(where, updates, model, name):
    collection = client.get_collection(name)
    query_dict = build_mongo_where_expression(where)
    collection.update_one(query_dict, {"$set": __convert_to_dict(updates)})
    return model.parse_obj(updates)


# equal create_or_update, To avoid multiple upserts, ensure that the filter fields are uniquely indexed.
def upsert_(where, updates, model, name):
    collections = client.get_collection(name)
    collections.update_one(build_mongo_where_expression(where), {"$set": __convert_to_dict(updates)}, upsert=True)
    return model.parse_obj(updates)


def update_one_with_condition(where, one, model, name):
    collections = client.get_collection(name)
    collections.update_one(build_mongo_where_expression(where), {"$set": __convert_to_dict(one)})


def update_(where, updates, model, name):
    collections = client.get_collection(name)
    collections.update_many(build_mongo_where_expression(where), {"$set": __convert_to_dict(updates)})


def pull_update(where, updates, model, name):
    collections = client.get_collection(name)
    collections.update_many(build_mongo_where_expression(where),
                            {"$pull": build_mongo_update_expression(__convert_to_dict(updates))})


def delete_by_id(id_, name):
    collection = client.get_collection(name)
    key = get_primary_key(name)
    collection.delete_one({key: id_})


def delete_one(where, name):
    collection = client.get_collection(name)
    collection.delete_one(build_mongo_where_expression(where))


def delete_(where, model, name):
    collection = client.get_collection(name)
    collection.delete_many(build_mongo_where_expression(where))


def find_by_id(id_, model, name):
    collections = client.get_collection(name)
    primary_key = get_primary_key(name)
    result = collections.find_one({primary_key: id_})
    if result is None:
        return
    else:
        return model.parse_obj(result)


def find_one(where: dict, model, name: str):
    collection = client.get_collection(name)
    result = collection.find_one(build_mongo_where_expression(where))
    if result is None:
        return
    else:
        return model.parse_obj(result)


def drop_(name: str):
    return client.get_collection(name).drop()


def find_(where: dict, model, name: str) -> list:
    collection = client.get_collection(name)
    cursor = collection.find(build_mongo_where_expression(where))
    result_list = list(cursor)
    return [model.parse_obj(result) for result in result_list]


def exists(where, model, name):
    collection = client.get_collection(name)
    result = collection.find_one(build_mongo_where_expression(where))
    if result is None:
        return False
    else:
        return True


def list_all(model, name: str):
    collection = client.get_collection(name)
    cursor = collection.find()
    result_list = list(cursor)
    return [model.parse_obj(result) for result in result_list]


def list_(where, model, name: str) -> list:
    collection = client.get_collection(name)
    cursor = collection.find(build_mongo_where_expression(where))
    result_list = list(cursor)
    return [model.parse_obj(result) for result in result_list]


def page_all(sort, pageable, model, name) -> DataPage:
    codec_options = build_code_options()
    collection = client.get_collection(name, codec_options=codec_options)
    total = collection.find().count()
    skips = pageable.pageSize * (pageable.pageNumber - 1)
    cursor = collection.find().skip(skips).limit(pageable.pageSize).sort(build_mongo_order(sort))
    return build_data_pages(pageable, [model.parse_obj(result) for result in list(cursor)], total)


def page_(where, sort, pageable, model, name) -> DataPage:
    codec_options = build_code_options()
    collection = client.get_collection(name, codec_options=codec_options)

    mongo_where = build_mongo_where_expression(where)
    total = collection.find(mongo_where).count()
    skips = pageable.pageSize * (pageable.pageNumber - 1)
    if sort is not None:
        cursor = collection.find(mongo_where).skip(skips).limit(pageable.pageSize).sort(
            build_mongo_order(sort))
    else:
        cursor = collection.find(mongo_where).skip(skips).limit(pageable.pageSize)
    if model is not None:
        return build_data_pages(pageable, [model.parse_obj(result) for result in list(cursor)], total)
    else:
        return build_data_pages(pageable, list(cursor), total)


def __convert_list_to_dict(items: list):
    result = []
    for item in items:
        result.append(__convert_to_dict(item))
    return result


def __convert_to_dict(instance) -> dict:
    if type(instance) is not dict:
        return instance.dict(by_alias=True)
    else:
        return instance


def find_one_and_update(where: dict, updates: dict, name: str):
    codec_options = build_code_options()
    collection = client.get_collection(name, codec_options=codec_options)
    return collection.find_one_and_update(filter=build_mongo_where_expression(where), update=updates, upsert=True)


'''
for topic data impl
'''


def create_topic_data_table(topic):
    pass


def alter_topic_data_table(topic):
    pass


def drop_topic_data_table(name):
    topic_name = build_collection_name(name)
    client.get_collection(topic_name).drop()


def topic_data_delete_(where, name):
    collection = client.get_collection(build_collection_name(name))
    if where is None:
        collection.drop()
    else:
        collection.delete_many(build_mongo_where_expression(where))


# save_topic_instance, insert one
def topic_data_insert_one(one, topic_name):
    codec_options = build_code_options()
    topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
    encode_dict(one)
    topic_data_col.insert(build_mongo_updates_expression_for_insert(one))
    return topic_name, one


def encode_dict(one):
    for k, v in one.items():
        if isinstance(v, date):
            one[k] = arrow.get(v).datetime


# save_topic_instances, insert many
def topic_data_insert_(data, topic_name):
    codec_options = build_code_options()
    topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
    for d in data:
        encode_dict(d)
    topic_data_col.insert_many(data)


def raw_topic_data_insert_one(one, topic_name):
    codec_options = build_code_options()
    topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
    topic_data_col.insert(one)


def topic_data_update_one(id_, one, topic_name):
    codec_options = build_code_options()
    topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
    encode_dict(one)
    topic_data_col.update_one({"_id": ObjectId(id_)},  build_mongo_updates_expression_for_update(one))


def topic_data_update_one_with_version(id_: str, version_: int, one: any, topic_name: str):
    # todo
    # find and modify
    topic_data_update_one(id_, one, topic_name)


def topic_data_update_(where, updates, name):
    codec_options = build_code_options()
    encode_dict(updates)
    collection = client.get_collection(build_collection_name(name), codec_options=codec_options)
    collection.update_many(build_mongo_where_expression(where), {"$set": __convert_to_dict(updates)})


def topic_data_find_by_id(id_, topic_name):
    codec_options = build_code_options()
    topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
    result = topic_data_col.find_one({"_id": ObjectId(id_)})
    return result


def topic_data_find_one(where, topic_name):
    codec_options = build_code_options()
    topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
    return topic_data_col.find_one(build_mongo_where_expression(where))


def topic_data_find_(where, topic_name):
    codec_options = build_code_options()
    topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
    return topic_data_col.find(build_mongo_where_expression(where))


def topic_data_list_all(topic_name) -> list:
    codec_options = build_code_options()
    topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
    result = topic_data_col.find()
    return list(result)


def topic_find_one_and_update(where: dict, updates: dict, name: str):
    codec_options = build_code_options()
    collection = client.get_collection(build_collection_name(name), codec_options=codec_options)
    return collection.find_one_and_update(filter=build_mongo_where_expression(where), update=updates, upsert=True,
                                          return_document=ReturnDocument.AFTER)


def topic_data_page_(where, sort, pageable, model, name) -> DataPage:
    return page_(build_mongo_where_expression(where), sort, pageable, model, name)


'''
special for raw_pipeline_monitor, need refactor for raw topic schema structure, ToDo
'''


def create_raw_pipeline_monitor():
    pass


def clear_metadata():
    pass
