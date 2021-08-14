from pymongo import MongoClient

from watchmen.database.datasource.data_source import DataSource


class MongoEngine(object):
    engine = None

    def __init__(self, datasource: DataSource):
        client = MongoClient(datasource.host, int(datasource.port), username=datasource.username,
                             password=datasource.password)
        self.engine = client[datasource.name]

    def get_engine(self):
        return self.engine
