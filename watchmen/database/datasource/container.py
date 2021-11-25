from typing import List, Dict

from storage.model.data_source import DataSource
from storage.storage.engine_adaptor import get_default_datasource

from watchmen.common.cache.cache_manage import DATA_SOURCE_LIST, cacheman
from watchmen.database.datasource.storage.data_source_storage import list_all_data_source_list
from watchmen.database.singleton import singleton
from watchmen.database.topic.mongo.topic_mongo_template import MongoTopicStorage
from watchmen.database.topic.mysql.topic_mysql_template import MysqlTopicStorage
from watchmen.database.topic.oracle.topic_oracle_template import OracleTopicStorage

DEFAULT_STORAGE = "DEFAULT_STORAGE"


@singleton
class DataSourceContainer(object):
    data_source_dict: Dict = {}

    def __init__(self):
        self.init()

    def init(self):
        data_source_list: List[DataSource] = list_all_data_source_list()
        for data_source in data_source_list:
            self.data_source_dict[data_source.dataSourceId] = data_source

    def get_data_source_by_id(self, datasource_id):
        if datasource_id is None:
            return None
        else:
            return self.data_source_dict[datasource_id]

    def clear_data_source_list(self):
        self.data_source_dict.clear()

    def reload_data_source_list(self):
        data_source_list: List[DataSource] = self.load_data_source_list()
        for data_source in data_source_list:
            self.data_source_dict[data_source.dataSourceId] = data_source

    @staticmethod
    def build_storage(datasource: DataSource):
        if datasource.dataSourceType == "mongodb":
            from storage.mongo.mongo_client import MongoEngine
            engine = MongoEngine(datasource)
            return MongoTopicStorage(client=engine.get_engine())
        elif datasource.dataSourceType == "mysql":
            from storage.mysql.mysql_client import MysqlEngine
            engine = MysqlEngine(datasource)
            return MysqlTopicStorage(client=engine.get_engine())
        elif datasource.dataSourceType == "oracle":
            from storage.oracle.oracle_client import OracleEngine
            engine = OracleEngine(datasource)
            return OracleTopicStorage(client=engine.get_engine())

    def get_storage(self, datasource_id):
        if datasource_id is None:
            return self.get_default_storage()
        else:
            return self.get_topic_storage(datasource_id)

    def get_topic_storage(self, datasource_id):
        storage = cacheman[DATA_SOURCE_LIST].get(datasource_id)
        if storage is not None:
            # print("load from cache: {}".format(storage))
            return storage
        else:
            storage = self.build_storage(self.get_data_source_by_id(datasource_id))
            cacheman[DATA_SOURCE_LIST].set(datasource_id, storage)
            return storage

    def get_default_storage(self):
        storage = cacheman[DATA_SOURCE_LIST].get(DEFAULT_STORAGE)
        if storage is not None:
            return storage
        else:
            default_datasource = get_default_datasource()
            storage = self.build_storage(default_datasource)
            cacheman[DATA_SOURCE_LIST].set(DEFAULT_STORAGE, storage)
            return storage


data_source_container = DataSourceContainer()
