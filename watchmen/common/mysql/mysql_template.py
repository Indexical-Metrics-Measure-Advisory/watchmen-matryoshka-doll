from watchmen.common.mysql.model.console_subject import create_console_subject, find_one_console_subject
from watchmen.common.mysql.model.raw_data_schema import create_raw_topic_schema, update_raw_topic_schema
from watchmen.common.storage.collection_list import CollectionList
from watchmen.common.mysql.model.topic_schema import create_topic_schema, update_topic_schema, \
    query_topic_schema_with_pagination, find_one_topic_schema
from watchmen.common.utils.data_utils import build_data_pages


print("mysql in")




create_switcher = {
    CollectionList.raw_schema: create_raw_topic_schema,
    CollectionList.console_subject: create_console_subject,
    CollectionList.topics: create_topic_schema
    # 1: one,
    # 2: lambda: 'two'
}

update_switcher = {
    CollectionList.raw_schema: update_raw_topic_schema,
    CollectionList.topics: update_topic_schema
}

remove_switcher = {

}

find_one_switcher = {
    CollectionList.console_subject: find_one_console_subject,
    CollectionList.topics: find_one_topic_schema
}

query_with_pagination_switcher = {
    CollectionList.topics: query_topic_schema_with_pagination
}


def select_collection_create_method(collection_name, instance):
    func = create_switcher.get(collection_name, lambda: 'Invalid Collection')
    return func(instance)


def select_collection_update_method(collection_name, query_dict, instance):
    func = update_switcher.get(collection_name, lambda: 'Invalid Collection')
    return func(query_dict, instance)


def select_collection_find_one_method(collection_name, query_dict):
    func = find_one_switcher.get(collection_name, lambda: 'Invalid Collection')
    return func(query_dict)


def select_collection_qwp_method(collection_name, pagination, query_dict, sort_dict):
    func = query_with_pagination_switcher.get(collection_name, lambda: 'Invalid Collection')
    return func(pagination, query_dict, sort_dict)


def create(collection_name, instance, base_model):
    select_collection_create_method(collection_name, instance)
    return base_model.parse_obj(instance)


def update_one(collection_name, query_dict, instance, base_model):
    select_collection_update_method(collection_name, query_dict, instance)
    return base_model.parse_obj(instance)


#only for mysql to partial update of JSON values
def update_one_of_partial(collection_name, query_dict, instance, base_model):
    pass

'''
def remove(collection_name, query_dict):
    collections = client.get_collection(collection_name)
    collections.remove(query_dict)
'''


def find_one(collection_name, query_dict, base_model):
    result = select_collection_find_one_method(collection_name, query_dict)
    if result is None:
        return
    else:
        return base_model.parse_obj(result)


def query_with_pagination(collection_name, pagination, base_model, query_dict=None, sort_dict=None):
    result = select_collection_qwp_method(collection_name, pagination, query_dict, sort_dict)
    return build_data_pages(pagination, [base_model.parse_obj(record) for record in result], 100)