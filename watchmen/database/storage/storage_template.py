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


def get_topic_factors(topic_name):
    return template.get_topic_factors(topic_name)


def check_topic_type(topic_name):
    return template.check_topic_type(topic_name)


def get_table_column_default_value(table_name, column_name):
    return template.get_table_column_default_value(table_name, column_name)


def clear_metadata():
    template.clear_metadata()
