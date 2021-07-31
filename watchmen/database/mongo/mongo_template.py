import datetime
import logging
from datetime import date

import arrow
import pymongo
from bson import regex, ObjectId
from pymongo import ReturnDocument

from watchmen.common.cache.cache_manage import cacheman, TOPIC_DICT_BY_NAME
from watchmen.common.data_page import DataPage
from watchmen.common.utils.data_utils import build_data_pages, build_collection_name
from watchmen.database.mongo.index import build_code_options, get_client
from watchmen.database.singleton import singleton
from watchmen.database.storage.storage_interface import StorageInterface
from watchmen.database.storage.utils.table_utils import get_primary_key

client = get_client()

log = logging.getLogger("app." + __name__)

log.info("mongo template initialized")


@singleton
class MongoStorage(StorageInterface):

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
                    new_updates["$set"][key] = value["_avg"]
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

    def insert_one(self, one, model, name):
        collection = client.get_collection(name)
        collection.insert_one(self.__convert_to_dict(one))
        return model.parse_obj(one)

    def insert_all(self, data, model, name):
        collection = client.get_collection(name)
        collection.insert_many(self.__convert_list_to_dict(data))
        return data

    def update_one(self, one, model, name) -> any:
        collection = client.get_collection(name)
        primary_key = get_primary_key(name)
        one_dict = self.__convert_to_dict(one)
        query_dict = {primary_key: one_dict.get(primary_key)}
        collection.update_one(query_dict, {"$set": one_dict})
        return model.parse_obj(one)

    def update_one_first(self, where, updates, model, name):
        collection = client.get_collection(name)
        query_dict = self.build_mongo_where_expression(where)
        collection.update_one(query_dict, {"$set": self.__convert_to_dict(updates)})
        return model.parse_obj(updates)

    def update_one_with_condition(self, where, one, model, name):
        collections = client.get_collection(name)
        collections.update_one(self.build_mongo_where_expression(where), {"$set": self.__convert_to_dict(one)})

    def update_(self, where, updates, model, name):
        collections = client.get_collection(name)
        collections.update_many(self.build_mongo_where_expression(where), {"$set": self.__convert_to_dict(updates)})

    def pull_update(self, where, updates, model, name):
        collections = client.get_collection(name)
        collections.update_many(self.build_mongo_where_expression(where),
                                {"$pull": self.build_mongo_update_expression(self.__convert_to_dict(updates))})

    def delete_by_id(self, id_, name):
        collection = client.get_collection(name)
        key = get_primary_key(name)
        collection.delete_one({key: id_})

    def delete_one(self, where, name):
        collection = client.get_collection(name)
        collection.delete_one(self.build_mongo_where_expression(where))

    def delete_(self, where, model, name):
        collection = client.get_collection(name)
        collection.delete_many(self.build_mongo_where_expression(where))

    def find_by_id(self, id_, model, name):
        collections = client.get_collection(name)
        primary_key = get_primary_key(name)
        result = collections.find_one({primary_key: id_})
        if result is None:
            return
        else:
            return model.parse_obj(result)

    def find_one(self, where: dict, model, name: str):
        collection = client.get_collection(name)
        result = collection.find_one(self.build_mongo_where_expression(where))
        if result is None:
            return
        else:
            return model.parse_obj(result)

    def drop_(self, name: str):
        return client.get_collection(name).drop()

    def find_(self, where: dict, model, name: str) -> list:
        collection = client.get_collection(name)
        cursor = collection.find(self.build_mongo_where_expression(where))
        result_list = list(cursor)
        return [model.parse_obj(result) for result in result_list]

    def list_all(self, model, name: str):
        collection = client.get_collection(name)
        cursor = collection.find()
        result_list = list(cursor)
        return [model.parse_obj(result) for result in result_list]

    def list_(self, where, model, name: str) -> list:
        collection = client.get_collection(name)
        cursor = collection.find(self.build_mongo_where_expression(where))
        result_list = list(cursor)
        return [model.parse_obj(result) for result in result_list]

    def page_all(self, sort, pageable, model, name) -> DataPage:
        codec_options = build_code_options()
        collection = client.get_collection(name, codec_options=codec_options)
        total = collection.find().count()
        skips = pageable.pageSize * (pageable.pageNumber - 1)
        cursor = collection.find().skip(skips).limit(pageable.pageSize).sort(self.build_mongo_order(sort))
        return build_data_pages(pageable, [model.parse_obj(result) for result in list(cursor)], total)

    def page_(self, where, sort, pageable, model, name) -> DataPage:
        codec_options = build_code_options()
        collection = client.get_collection(name, codec_options=codec_options)

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
            for doc in cursor:
                del doc['_id']
                results.append(doc)
            return build_data_pages(pageable, results, total)

    def __convert_list_to_dict(self, items: list):
        result = []
        for item in items:
            result.append(self.__convert_to_dict(item))
        return result

    def __convert_to_dict(self, instance) -> dict:
        if type(instance) is not dict:
            return instance.dict(by_alias=True)
        else:
            return instance

    '''
    for topic data impl
    '''

    def drop_topic_data_table(self, name):
        topic_name = build_collection_name(name)
        client.get_collection(topic_name).drop()

    def topic_data_delete_(self, where, name):
        collection = client.get_collection(build_collection_name(name))
        if where is None:
            collection.drop()
        else:
            collection.delete_many(self.build_mongo_where_expression(where))

    def topic_data_insert_one(self, one, topic_name):
        codec_options = build_code_options()
        topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        self.encode_dict(one)
        topic_data_col.insert(self.build_mongo_updates_expression_for_insert(one))
        return topic_name, one

    def encode_dict(self, one):
        for k, v in one.items():
            if isinstance(v, date):
                one[k] = arrow.get(v).datetime

    def topic_data_insert_(self, data, topic_name):
        codec_options = build_code_options()
        topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        for d in data:
            self.encode_dict(d)
        topic_data_col.insert_many(data)

    def topic_data_update_one(self, id_, one, topic_name):
        codec_options = build_code_options()
        topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        self.encode_dict(one)
        topic_data_col.update_one({"_id": ObjectId(id_)}, self.build_mongo_updates_expression_for_update(one))

    def topic_data_update_one_with_version(self, id_, version_, one, topic_name):
        codec_options = build_code_options()
        topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        self.encode_dict(one)
        return topic_data_col.find_one_and_update(
            # filter=self.build_mongo_where_expression({"_id": ObjectId(id_), "version_": version_}),
            filter=self.build_mongo_where_expression({"_id": ObjectId(id_)}),
            update=self.build_mongo_updates_expression_for_update(one),
            upsert=False,
            return_document=ReturnDocument.AFTER)

    def topic_data_update_(self, where, updates, name):
        codec_options = build_code_options()
        self.encode_dict(updates)
        collection = client.get_collection(build_collection_name(name), codec_options=codec_options)
        collection.update_many(self.build_mongo_where_expression(where), {"$set": self.__convert_to_dict(updates)})

    def topic_data_find_by_id(self, id_, topic_name):
        codec_options = build_code_options()
        topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        result = topic_data_col.find_one({"_id": ObjectId(id_)})
        return result

    def topic_data_find_one(self, where, topic_name):
        codec_options = build_code_options()
        topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        return topic_data_col.find_one(self.build_mongo_where_expression(where))

    def topic_data_find_(self, where, topic_name):
        codec_options = build_code_options()
        topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        return topic_data_col.find(self.build_mongo_where_expression(where))

    def topic_data_find_with_aggregate(self, where, topic_name, aggregate):
        codec_options = build_code_options()
        topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        for key, value in aggregate.items():
            aggregate_ = {}
            if value == "sum":
                aggregate_ = {key: {"$sum": f'${key}'}}
            elif value == "count":
                return topic_data_col.count_documents(self.build_mongo_where_expression(where))
            elif value == "avg":
                aggregate_ = {key:  {"$avg": f'${key}'}}
        pipeline = [{"$match": self.build_mongo_where_expression(where)},{"$project": aggregate_}]
        result = topic_data_col.aggregate(pipeline)
        return result

    def topic_data_list_all(self, topic_name) -> list:
        codec_options = build_code_options()
        topic_data_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
        result = topic_data_col.find()
        return list(result)

    def topic_data_page_(self, where, sort, pageable, model, name) -> DataPage:
        topic_collection_name = build_collection_name(name)
        codec_options = build_code_options()
        collection = client.get_collection(topic_collection_name, codec_options=codec_options)

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
            if self._check_topic_type(name) == "raw":
                for doc in cursor:
                    results.append(doc['data_'])
            else:
                for doc in cursor:
                    del doc['_id']
                    results.append(doc)
            return build_data_pages(pageable, results, total)

    def _check_topic_type(self, topic_name):
        topic = self._get_topic(topic_name)
        return topic['type']

    def _get_topic(self, topic_name) -> any:
        if cacheman[TOPIC_DICT_BY_NAME].get(topic_name) is not None:
            return cacheman[TOPIC_DICT_BY_NAME].get(topic_name)
        codec_options = build_code_options()
        topic_collection = client.get_collection("topics", codec_options=codec_options)
        result = topic_collection.find_one({"name": topic_name})
        if result is None:
            raise Exception("not find topic {0}".format(topic_name))
        else:
            cacheman[TOPIC_DICT_BY_NAME].set(topic_name, result)
            return result

    def clear_metadata(self):
        pass
