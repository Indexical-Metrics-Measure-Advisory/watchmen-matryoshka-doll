from typing import List, Dict

from watchmen.common.cache.cache_manage import DATA_SOURCE_LIST, cacheman
from watchmen.database.datasource.data_source import DataSource
from watchmen.database.datasource.storage.data_source_storage import load_data_source_list
from watchmen.database.mongo.mongo_client import MongoEngine
from watchmen.database.mysql.mysql_client import MysqlEngine
from watchmen.database.oracle.oracle_client import OracleEngine
from watchmen.database.singleton import singleton
# contains all datasource definition
from watchmen.database.storage.engine_adaptor import get_default_datasource
from watchmen.database.topic.mongo.topic_mongo_template import MongoTopicStorage
from watchmen.database.topic.mysql.topic_mysql_template import MysqlTopicStorage

DEFAULT_STORAGE = "DEFAULT_STORAGE"


@singleton
class DataSourceContainer(object):
    data_source_dict: Dict = {}

    def __init__(self):
        # self.data_source_dict: Dict = {}
        self.init()

    def init(self):
        data_source_list: List[DataSource] = load_data_source_list()
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
        data_source_list: List[DataSource] = load_data_source_list()
        for data_source in data_source_list:
            self.data_source_dict[data_source.dataSourceId] = data_source

    @staticmethod
    def build_storage(datasource: DataSource):
        if datasource.dataSourceType == "mongodb":
            engine = MongoEngine(datasource)
            return MongoTopicStorage(client=engine.get_engine())
        elif datasource.dataSourceType == "mysql":
            engine = MysqlEngine(datasource)
            return MysqlTopicStorage(client=engine.get_engine())
        elif datasource.dataSourceType == "oracle":
            engine = OracleEngine(datasource)
            pass

    def get_storage(self, datasource_id):
        if datasource_id is None:
            return self.get_default_storage()
        else:
            return self.get_topic_storage(datasource_id)

    def get_topic_storage(self, datasource_id):
        storage = cacheman[DATA_SOURCE_LIST].get(datasource_id)
        if storage is not None:
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
