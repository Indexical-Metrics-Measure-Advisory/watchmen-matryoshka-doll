from pydantic.main import BaseModel

from watchmen.database.storage.engine_adaptor import find_template
from watchmen.database.storage.storage_interface import Pageable, DataPage

template = find_template()


def insert_one(one: any, model: BaseModel, name: str) -> BaseModel:
    return template.insert_one(one, model, name)


def insert_all(data: list, model: BaseModel, name: str):
    return template.insert_all(data, model, name)


def update_one(one: any, model: BaseModel, name: str) -> any:
    return template.update_one(one, model, name)


def update_one_first(where: dict, updates: dict, model: BaseModel, name: str) -> BaseModel:
    return template.update_one_first(where, updates, model, name)


def update_(where: dict, updates: dict, model: BaseModel, name: str):
    template.update_(where, updates, model, name)


def pull_update(where: dict, updates: dict, model: BaseModel, name: str):
    template.pull_update(where, updates, model, name)


def delete_by_id(id_: str, name: str):
    template.delete_by_id(id_, name)


def delete_one(where: dict, name: str):
    template.delete_one(where, name)


def delete_(where: dict, model: BaseModel, name: str):
    template.delete_(where, model, name)


def delete_all(model: BaseModel, name: str) -> list:
    raise NotImplementedError("delete_all not implemented")


def drop_(name: str):
    template.drop_(name)


def find_by_id(id_: str, model: BaseModel, name: str) -> BaseModel:
    return template.find_by_id(id_, model, name)


def find_one(where: dict, model: BaseModel, name: str) -> BaseModel:
    return template.find_one(where, model, name)


def find_(where: dict, model: BaseModel, name: str) -> list:
    return template.find_(where, model, name)


def list_all(model: BaseModel, name: str) -> list:
    return template.list_all(model, name)


def list_all_select(select: dict, model: BaseModel, name: str) -> list:
    pass  # need to do


def list_(where: dict, model: BaseModel, name: str) -> list:
    return template.list_(where, model, name)


def list_select(select: dict, where: dict, model: BaseModel, name: str) -> list:
    pass  # need to do


def page_all(sort: list, pageable: Pageable, model: BaseModel, name: str) -> DataPage:
    return template.page_all(sort, pageable, model, name)


def page_(where: dict, sort: list, pageable: Pageable, model: BaseModel, name: str) -> DataPage:
    return template.page_(where, sort, pageable, model, name)


'''
for topic data storage interface
'''


def topic_data_insert_one(one: any, topic_name: str) -> tuple:
    return template.topic_data_insert_one(one, topic_name)


def topic_data_insert_(data: list, topic_name: str):
    template.topic_data_insert_(data, topic_name)


def topic_data_delete_(where, name):
    template.topic_data_delete_(where, name)


def drop_topic_data_table(name):
    template.drop_topic_data_table(name)


def topic_data_update_one(id_: str, one: any, topic_name: str):
    template.topic_data_update_one(id_, one, topic_name)


def topic_data_update_one_with_version(id_: str, version_: int, one: any, topic_name: str):
    template.topic_data_update_one_with_version(id_, version_, one, topic_name)


def topic_data_update_(where: dict, updates: dict, name: str):
    template.topic_data_update_(where, updates, name)


def topic_data_find_by_id(id_: str, topic_name: str) -> any:
    return template.topic_data_find_by_id(id_, topic_name)


def topic_data_find_one(where: dict, topic_name: str) -> any:
    return template.topic_data_find_one(where, topic_name)


def topic_data_find_(where, topic_name):
    return template.topic_data_find_(where, topic_name)


def topic_data_find_with_aggregate(where, topic_name, aggregate):
    return template.topic_data_find_with_aggregate(where, topic_name, aggregate)


def topic_data_list_all(topic_name) -> list:
    return template.topic_data_list_all(topic_name)


def topic_data_page_(where: dict, sort: list, pageable: Pageable, model: BaseModel, name: str) -> DataPage:
    return template.topic_data_page_(where, sort, pageable, model, name)


def clear_metadata():
    template.clear_metadata()
