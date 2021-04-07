from enum import Enum
from typing import List

from pydantic.main import BaseModel

from watchmen.common.storage.engine_adaptor import find_template

template = find_template()


class OrderType(Enum):
    """Ascending sort order."""
    ASCENDING = 1
    """Descending sort order."""
    DESCENDING = -1

'''
class SqlOperator(Enum):
    AND = "and"
    OR = "or"
'''


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


def insert_all(data: list, model: BaseModel, name: str):
    template.insert_all(data, model, name)


def update_one(one: any, model: BaseModel, name: str) -> any:
    return template.update_one(one, model, name)


def update_one_first(where: dict, updates: dict, model: BaseModel, name: str) -> BaseModel:
    return template.update_one_first(where, updates, model, name)


def upsert_(where: dict, updates: dict, model: BaseModel, name: str) -> BaseModel:
    return template.upsert(where, updates, model, name)


def update_(where: dict, updates: dict, model: BaseModel, name: str):
    template.update_(where, updates, model, name)


def delete_one(id: str, name: str):
    template.delete_one(id, name)


def delete_(where: dict, model: BaseModel, name: str):
    template.delete(where, model, name)


def delete_all(model: BaseModel, name: str) -> list:
    pass  # don't need to do


def find_by_id(id_: str, model: BaseModel, name: str) -> BaseModel:
    return template.find_by_id(id_, model, name)


def find_one(where: dict, model: BaseModel, name: str) -> BaseModel:
    return template.find_one(where, model, name)


def find_(where: dict, model: BaseModel, name: str) -> list:
    return template.find_(where, model, name)


def exists(where: dict, model: BaseModel, name: str):
    return template.exists(where, model, name)


def list_all(model: BaseModel, name: str) -> list:
    return template.list_all(model, name)


def list_all_select(select: dict, model: BaseModel, name: str) -> list:
    pass  # need to do


def list_(where: dict, model: BaseModel, name: str) -> list:
    return template.list_(where, model, name)


def list_select(select: dict, where: dict, model: BaseModel, name: str) -> list:
    pass  # need to do


def page_all(sort: list, pageable: Pageable, model: BaseModel, name: str) -> DataPage:
    return template.page(sort, pageable, model, name)


def page_(where: dict, sort: list, pageable: Pageable, model: BaseModel, name: str) -> DataPage:
    return template.page_(where, sort, pageable, model, name)
