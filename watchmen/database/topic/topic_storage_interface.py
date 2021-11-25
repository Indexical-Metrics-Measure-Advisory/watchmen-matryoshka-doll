import abc

from pydantic.main import BaseModel
from storage.storage.storage_interface import Pageable, DataPage


class TopicStorageInterface(abc.ABC):

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
