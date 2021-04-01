from typing import List

from pydantic.main import BaseModel

from watchmen.common.storage.engine_adaptor import find_template

template = find_template()


class Pageable(BaseModel):
    pageSize: int = None
    pageNumber: int = None


class DataPage(BaseModel):
    data: List = []
    itemCount: int = None
    pageNumber: int = None
    pageSize: int = None
    pageCount: int = None


def insert_one(one: any, model: BaseModel, name: str) -> BaseModel:
    return template.insert_one(one, model, name)


def insert_all(data: list[any], model: BaseModel, name: str):
    template.insert_all(data, model, name)


def update_one(one: any, model: BaseModel, name: str) -> any:
    return template.update_one(one, model, name)


def update_one(where: dict, updates: dict, model: BaseModel, name: str) -> BaseModel:
    return template.update_one(where, updates, model, name)


def upsert(where: dict, updates: dict, model: BaseModel, name: str) -> BaseModel:
    return template.upsert(where, updates, model, name)


def update(where: dict, updates: dict, model: BaseModel, name: str):
    template.update(where, updates, model, name)


def delete_one(id: str, name: str):
    template.delete_one(id, name)


def delete(where: dict, model: BaseModel, name: str):
    template.delete(where, model, name)


def delete_all(model: BaseModel, name: str) -> list:
    pass  # don't need to do


def find_by_id(id: str, model: BaseModel, name: str) -> BaseModel:
    return template.find_by_id(id, model, name)


def find_one(where: dict, model: BaseModel, name: str) -> BaseModel:
    return template.find_one(where, model, name)


def exists(where: dict, model: BaseModel, name: str):
    return  # need to do


def list_all(model: BaseModel, name: str) -> list[BaseModel]:
    return template.list_all(model, name)


def list_all(select: dict, model: BaseModel, name: str) -> list[any]:
    pass


def list_(where: dict, model: BaseModel, name: str) -> list:
    return template.list_(where, model, name)


def list_(select: dict, where: dict, model: BaseModel, name: str) -> list:
    pass # need to do


def page(sort: list, pageable: Pageable, model: BaseModel, name: str) -> DataPage:
    return template.page(sort, pageable, model, name)


def page(where: dict, sort: list, pageable: Pageable, model: BaseModel, name: str) -> DataPage:
    return template.page(where, sort, pageable, model, name)


