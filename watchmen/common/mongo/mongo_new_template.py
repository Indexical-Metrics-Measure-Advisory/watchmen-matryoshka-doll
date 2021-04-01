import logging

from watchmen.common.data_page import DataPage
from watchmen.common.mongo.index import build_code_options
from watchmen.common.mysql.model.table_definition import get_primary_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_data_pages

client = get_client()

log = logging.getLogger("app." + __name__)

log.info("mongo template initialized")


def build_mongo_query(where: dict):
    return where


def insert_one(one, model, name):
    collection = client.get_collection(name)
    collection.insert_one(__convert_to_dict(one))
    return model.parse_obj(one)


def insert_all(data, model, name):
    collection = client.get_collection(name)
    collection.insert_many(__convert_to_dict(data))


def update_one(one, model, name) -> any:
    collection = client.get_collection(name)
    primary_key = get_primary_key(name)
    one_dict = __convert_to_dict(one)
    query_dict = {primary_key: one_dict.get(primary_key)}
    collection.update_one(query_dict, {"$set": one_dict})
    return model.parse_obj(one)


def update_one(where, updates, model, name):
    collection = client.get_collection(name)
    query_dict = build_mongo_query(where)
    collection.update_one(query_dict, {"$set": updates})
    return model.parse_obj(updates)


# equal create_or_update, To avoid multiple upserts, ensure that the filter fields are uniquely indexed.
def upsert(where, updates, model, name: str):
    collections = client.get_collection(name)
    collections.update_one(where, {"$set": __convert_to_dict(updates)}, upsert=True)
    return model.parse_obj(updates)


def update(where, updates, model, name):
    collection = client.get_collection(name)
    collection.update_many(where, updates)


def delete_one(id, name):
    collection = client.get_collection(name)
    key = get_primary_key(name)
    collection.delete_one({key: id})


def delete(where, model, name):
    collection = client.get_collection(name)
    collection.remove(where)


def find_by_id(id, model, name):
    collections = client.get_collection(name)
    primary_key = get_primary_key(name)
    result = collections.find_one({primary_key: id})
    if result is None:
        return
    else:
        return model.parse_obj(result)


def find_one(where: dict, model, name: str):
    collection = client.get_collection(name)
    result = collection.find_one(where)
    if result is None:
        return
    else:
        return model.parse_obj(result)


def list_all(model, name: str):
    collection = client.get_collection(name)
    cursor = collection.find()
    result_list = list(cursor)
    return [model.parse_obj(result) for result in result_list]


def list_(where, model, name: str) -> list:
    collection = client.get_collection(name)
    cursor = collection.find(where)
    result_list = list(cursor)
    return [model.parse_obj(result) for result in result_list]


def page(sort, pageable, model, name) -> DataPage:
    codec_options = build_code_options()
    collection = client.get_collection(name, codec_options=codec_options)
    total = collection.find().count()
    skips = pageable.pageSize * (pageable.pageNumber - 1)
    cursor = collection.find().skip(skips).limit(pageable.pageSize).sort(*sort)
    return build_data_pages(pageable, [model.parse_obj(result) for result in list(cursor)], total)


def page(where, sort, pageable, model, name) -> DataPage:
    codec_options = build_code_options()
    collection = client.get_collection(name, codec_options=codec_options)
    total = collection.find(where).count()
    skips = pageable.pageSize * (pageable.pageNumber - 1)
    cursor = collection.find(where).skip(skips).limit(pageable.pageSize).sort(*sort)
    return build_data_pages(pageable, [model.parse_obj(result) for result in list(cursor)], total)


def __convert_to_dict(instance) -> dict:
    if type(instance) is not dict:
        return instance.dict()
    else:
        return instance


def find_one_and_update(where: dict, updates: dict, name: str):
    collection = client.get_collection(name)
    return collection.find_one_and_update(filter=where, update=updates)
