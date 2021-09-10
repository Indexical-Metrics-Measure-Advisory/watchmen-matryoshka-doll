import logging
from datetime import date

import arrow
import pymongo
from bson import regex, ObjectId
from pymongo.errors import WriteError

from watchmen.common.cache.cache_manage import cacheman, TOPIC_DICT_BY_NAME
from watchmen.common.data_page import DataPage
from watchmen.common.utils.data_utils import build_data_pages, build_collection_name
from watchmen.database.mongo.index import build_code_options
from watchmen.database.storage import storage_template
from watchmen.database.storage.exception.exception import OptimisticLockError, InsertConflictError
from watchmen.database.topic.topic_storage_interface import TopicStorageInterface

log = logging.getLogger("app." + __name__)




# @singleton
class MongoTopicStorage(TopicStorageInterface):
    client = None

    def __init__(self, client):
        self.client = client
        log.info("mongo template initialized")

    def build_mongo_where_expression(self, where: dict):
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
                        result = self.build_mongo_where_expression(express)
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
                        if k == "not-in":
                            return {key: {"$nin": v}}
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

    def build_mongo_update_expression(self, updates):
        """
        # used in pull_update, just allowed to update one field
        """
        for key, value in updates.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    if k == "in":
                        return {key: {"$in": v}}

    def build_mongo_updates_expression_for_insert(self, updates):
        new_updates = {}
        for key, value in updates.items():
            if isinstance(value, dict):
                if "_sum" in value:
                    new_updates[key] = value["_sum"]
                elif "_count" in value:
                    new_updates[key] = value["_count"]
                elif "_avg" in value:
                    new_updates[key] = value["_avg"]
                else:
                    new_updates[key] = value
            else:
                new_updates[key] = value
        return new_updates

    def build_mongo_updates_expression_for_update(self, updates):
        new_updates = {}
        new_updates["$set"] = {}
        for key, value in updates.items():
            if isinstance(value, dict):
                if "_sum" in value:
                    new_updates['$inc'] = {key: value["_sum"]}
                elif "_count" in value:
                    new_updates['$inc'][key] = value["_count"]
                elif "_avg" in value:
                    pass
                else:
                    new_updates["$set"][key] = value
            else:
                if key == "version_":
                    new_updates["$set"][key] = updates.get(key) + 1
                else:
                    new_updates["$set"][key] = value
        return new_updates

    def build_mongo_order(self, order_: list):
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

    '''
    for topic data impl
    '''

    def drop_topic_data_table(self, name):
        topic_name = build_collection_name(name)
        self.client.get_collection(topic_name).drop()

    def topic_data_delete_(self, where, name):
        collection = self.client.get_collection(build_collection_name(name))
        if where is None:
            collection.drop()
        else:
            collection.delete_many(self.build_mongo_where_expression(where))

    def topic_data_insert_one(self, one, topic_name):
        codec_options = build_code_options()
        topic_data_col = self.client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        self.encode_dict(one)
        try:
            result = topic_data_col.insert_one(self.build_mongo_updates_expression_for_insert(one))
        except WriteError as we:
            if we.code == 11000:  # E11000 duplicate key error
                raise InsertConflictError("InsertConflict")
        return result.inserted_id

    def encode_dict(self, one):
        for k, v in one.items():
            if isinstance(v, date):
                one[k] = arrow.get(v).datetime

    def topic_data_insert_(self, data, topic_name):
        codec_options = build_code_options()
        topic_data_col = self.client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        for d in data:
            self.encode_dict(d)
        topic_data_col.insert_many(data)

    def topic_data_update_one(self, id_, one, topic_name):
        codec_options = build_code_options()
        topic_data_col = self.client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        self.encode_dict(one)
        topic_data_col.update_one({"_id": ObjectId(id_)}, self.build_mongo_updates_expression_for_update(one))

    def topic_data_update_one_with_version(self, id_, version_, one, topic_name):
        codec_options = build_code_options()
        topic_data_col = self.client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        self.encode_dict(one)
        result = topic_data_col.update_one(
            self.build_mongo_where_expression({"_id": ObjectId(id_), "version_": version_}),
            self.build_mongo_updates_expression_for_update(one))
        if result.modified_count == 0:
            raise OptimisticLockError("Optimistic lock error")

    def topic_data_update_(self, where, updates, name):
        codec_options = build_code_options()
        self.encode_dict(updates)
        collection = self.client.get_collection(build_collection_name(name), codec_options=codec_options)
        collection.update_many(self.build_mongo_where_expression(where), {"$set": self.__convert_to_dict(updates)})

    def topic_data_find_by_id(self, id_, topic_name):
        codec_options = build_code_options()
        topic_data_col = self.client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        result = topic_data_col.find_one({"_id": ObjectId(id_)})
        return result

    def topic_data_find_one(self, where, topic_name):
        codec_options = build_code_options()
        topic_data_col = self.client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        return topic_data_col.find_one(self.build_mongo_where_expression(where))

    def topic_data_find_(self, where, topic_name):
        codec_options = build_code_options()
        topic_data_col = self.client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        return topic_data_col.find(self.build_mongo_where_expression(where))

    def topic_data_find_with_aggregate(self, where, topic_name, aggregate):
        codec_options = build_code_options()
        topic_data_col = self.client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        for key, value in aggregate.items():
            aggregate_ = {}
            if value == "sum":
                aggregate_ = {"$group":
                    {
                        "_id": "null",
                        "value": {"$sum": f'${key}'}
                    }
                }
            elif value == "count":
                return topic_data_col.count_documents(self.build_mongo_where_expression(where))
            elif value == "avg":
                aggregate_ = {"$group":
                    {
                        "_id": "null",
                        "value": {"$avg": f'${key}'}
                    }
                }
        pipeline = [{"$match": self.build_mongo_where_expression(where)}, aggregate_]
        cursor = topic_data_col.aggregate(pipeline)
        for doc in cursor:
            result = doc["value"]
            return result

    def topic_data_list_all(self, topic_name) -> list:
        codec_options = build_code_options()
        topic_data_col = self.client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        result = topic_data_col.find()
        return list(result)

    def topic_data_page_(self, where, sort, pageable, model, name) -> DataPage:
        topic_collection_name = build_collection_name(name)
        codec_options = build_code_options()
        collection = self.client.get_collection(topic_collection_name, codec_options=codec_options)

        mongo_where = self.build_mongo_where_expression(where)
        total = collection.find(mongo_where).count()
        skips = pageable.pageSize * (pageable.pageNumber - 1)
        if sort is not None:
            cursor = collection.find(mongo_where).skip(skips).limit(pageable.pageSize).sort(
                self.build_mongo_order(sort))
        else:
            cursor = collection.find(mongo_where).skip(skips).limit(pageable.pageSize)
        if model is not None:
            return build_data_pages(pageable, [model.parse_obj(result) for result in list(cursor)], total)
        else:
            results = []
            if storage_template.check_topic_type(name) == "raw":
                for doc in cursor:
                    results.append(doc['data_'])
            else:
                for doc in cursor:
                    del doc['_id']
                    results.append(doc)
            return build_data_pages(pageable, results, total)

    def clear_metadata(self):
        pass
