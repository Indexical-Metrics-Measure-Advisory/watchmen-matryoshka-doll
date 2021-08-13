from pydantic import BaseModel

from watchmen.database.storage.storage_interface import Pageable, DataPage


class TopicStorageEngine(object):

    template = None

    def __init__(self,template):
        self.template = template

    def topic_data_insert_one(self,one: any, topic_name: str) -> tuple:
        return self.template.topic_data_insert_one(one, topic_name)

    def topic_data_insert_(self,data: list, topic_name: str):
        return self.template.topic_data_insert_(data, topic_name)

    def topic_data_delete_(self,where, name):
        return self.template.topic_data_delete_(where, name)

    def drop_topic_data_table(self,name):
        return self.template.drop_topic_data_table(name)

    def topic_data_update_one(self,id_: str, one: any, topic_name: str):
        return self.template.topic_data_update_one(id_, one, topic_name)

    def topic_data_update_one_with_version(self,id_: str, version_: int, one: any, topic_name: str):
        return self.template.topic_data_update_one_with_version(id_, version_, one, topic_name)

    def topic_data_update_(self,where: dict, updates: dict, name: str):
        return self.template.topic_data_update_(where, updates, name)

    def topic_data_find_by_id(self,id_: str, topic_name: str) -> any:
        return self.template.topic_data_find_by_id(id_, topic_name)

    def topic_data_find_one(self,where: dict, topic_name: str) -> any:
        return self.template.topic_data_find_one(where, topic_name)

    def topic_data_find_(self,where, topic_name):
        return self.template.topic_data_find_(where, topic_name)

    def topic_data_find_with_aggregate(self,where, topic_name, aggregate):
        return self.template.topic_data_find_with_aggregate(where, topic_name, aggregate)

    def topic_data_list_all(self,topic_name) -> list:
        return self.template.topic_data_list_all(topic_name)

    def topic_data_page_(self,where: dict, sort: list, pageable: Pageable, model: BaseModel, name: str) -> DataPage:
        return self.template.topic_data_page_(where, sort, pageable, model, name)




