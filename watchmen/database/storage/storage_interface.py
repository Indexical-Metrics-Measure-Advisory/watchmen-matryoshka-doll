import abc
from enum import Enum
from typing import List

from pydantic.main import BaseModel


class OrderType(Enum):
    """Ascending sort order."""
    ASCENDING = 1
    """Descending sort order."""
    DESCENDING = -1


class Pageable(BaseModel):
    pageSize: int = None
    pageNumber: int = None


class DataPage(BaseModel):
    data: List = []
    itemCount: int = None
    pageNumber: int = None
    pageSize: int = None
    pageCount: int = None


class StorageInterface(abc.ABC):

    @abc.abstractmethod
    def insert_one(self, one: any, model: BaseModel, name: str) -> BaseModel:
        pass

    @abc.abstractmethod
    def insert_all(self, data: list, model: BaseModel, name: str):
        pass

    @abc.abstractmethod
    def update_one(self, one: any, model: BaseModel, name: str) -> any:
        pass

    #
    # @abc.abstractmethod
    # def update_one_with_field(self,one: any, model: BaseModel, name: str, where: dict):
    #     pass

    @abc.abstractmethod
    def update_one_first(self, where: dict, updates: dict, model: BaseModel, name: str) -> BaseModel:
        pass

    @abc.abstractmethod
    def update_(self, where: dict, updates: dict, model: BaseModel, name: str):
        pass

    @abc.abstractmethod
    def pull_update(self, where: dict, updates: dict, model: BaseModel, name: str):
        pass

    @abc.abstractmethod
    def delete_by_id(self, id_: str, name: str):
        pass

    @abc.abstractmethod
    def delete_one(self, where: dict, name: str):
        pass

    @abc.abstractmethod
    def delete_(self, where: dict, model: BaseModel, name: str):
        pass

    # @abc.abstractmethod
    # def delete_all(self,model: BaseModel, name: str) -> licreate_topic_data_table_indexst:
    #     pass

    @abc.abstractmethod
    def drop_(self, name: str):
        pass

    @abc.abstractmethod
    def find_by_id(self, id_: str, model: BaseModel, name: str) -> BaseModel:
        pass

    @abc.abstractmethod
    def find_one(self, where: dict, model: BaseModel, name: str) -> BaseModel:
        pass

    @abc.abstractmethod
    def find_(self, where: dict, model: BaseModel, name: str) -> list:
        pass

    # @abc.abstractmethod
    # def exists(self,where: dict, model: BaseModel, name: str):
    #     pass

    @abc.abstractmethod
    def list_all(self, model: BaseModel, name: str) -> list:
        pass

    # @abc.abstractmethod
    # def list_all_select(self,select: dict, model: BaseModel, name: str) -> list:
    #     pass  # need to do

    @abc.abstractmethod
    def list_(self, where: dict, model: BaseModel, name: str) -> list:
        pass

    # @abc.abstractmethod
    # def list_select(self,select: dict, where: dict, model: BaseModel, name: str) -> list:
    #     pass  # need to do

    @abc.abstractmethod
    def page_all(self, sort: list, pageable: Pageable, model: BaseModel, name: str) -> DataPage:
        pass

    @abc.abstractmethod
    def page_(self, where: dict, sort: list, pageable: Pageable, model: BaseModel, name: str) -> DataPage:
        pass

    '''
    for topic data storage interface
    '''

    @abc.abstractmethod
    def topic_data_insert_one(self, one: any, topic_name: str) -> tuple:
        pass

    @abc.abstractmethod
    def topic_data_insert_(self, data: list, topic_name: str):
        pass

    @abc.abstractmethod
    def topic_data_delete_(self, where, name):
        pass

    @abc.abstractmethod
    def drop_topic_data_table(self, name):
        pass

    @abc.abstractmethod
    def topic_data_update_one(self, id_: str, one: any, topic_name: str):
        pass

    def topic_data_update_one_with_version(self, id_: str, version_: int, one: any, topic_name: str):
        pass

    @abc.abstractmethod
    def topic_data_update_(self, where: dict, updates: dict, name: str):
        pass

    @abc.abstractmethod
    def topic_data_find_by_id(self, id_: str, topic_name: str) -> any:
        pass

    @abc.abstractmethod
    def topic_data_find_one(self, where: dict, topic_name: str) -> any:
        pass

    @abc.abstractmethod
    def topic_data_find_(self, where, topic_name):
        pass

    @abc.abstractmethod
    def topic_data_find_with_aggregate(self, where, topic_name, aggregate):
        pass

    @abc.abstractmethod
    def topic_data_list_all(self, topic_name) -> list:
        pass

    @abc.abstractmethod
    def topic_data_page_(self, where: dict, sort: list, pageable: Pageable, model: BaseModel, name: str) -> DataPage:
        pass

    @abc.abstractmethod
    def clear_metadata(self):
        pass
