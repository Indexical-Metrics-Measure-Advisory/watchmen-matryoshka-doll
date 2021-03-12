from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_data_pages

client = get_client()


def create(collection_name, instance, base_model):
    collections = client.get_collection(collection_name)
    collections.insert_one(__convert_to_dict(instance))
    return base_model.parse_obj(instance)


def update_one(collection_name,query_dict,instance,base_model):
    collections = client.get_collection(collection_name)
    collections.update_one(query_dict,{"$set":__convert_to_dict(instance)})
    return base_model.parse_obj(instance)


def find_one(collection_name,query_dict,base_model):
    collections = client.get_collection(collection_name)
    result = collections.find_one(query_dict)
    if result is None:
        return
    else:
        return base_model.parse_obj(result)


def find(collection_name,query_dict,base_model, sort_dict=None):
    collections = client.get_collection(collection_name)
    cursor = collections.find(query_dict)
    result_list = list(cursor)
    return [base_model.parse_obj(result) for result in result_list]


def __find_with_count(collections,query_dict):
    return collections.find(query_dict).count()


def query_with_pagination(collection_name,query_dict,pagination,base_model):
    collections = client.get_collection(collection_name)
    items_count = __find_with_count(collections,query_dict)
    skips = pagination.pageSize * (pagination.pageNumber - 1)
    cursor = collections.find(query_dict).skip(skips).limit(pagination.pageSize)
    result_list = list(cursor)
    return build_data_pages(pagination,[base_model.parse_obj(result) for result in result_list],items_count)


def __convert_to_dict(instance):
    if type(instance) is not dict:
        return instance.dict()
    else:
        return instance
