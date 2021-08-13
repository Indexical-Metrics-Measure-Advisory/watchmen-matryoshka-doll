from watchmen.config.config import settings
from watchmen.database.datasource.data_source import DataSource
from watchmen.database.mongo.mongo_client import MongoEngine
from watchmen.database.mysql.mysql_client import MysqlEngine

MYSQL = "mysql"
MONGO = "mongo"
ORACLE = "oracle"


def get_default_datasource():
    datasource = DataSource()
    datasource.dataSourceCode = "default"
    datasource.dataSourceType = settings.STORAGE_ENGINE
    if settings.STORAGE_ENGINE == MONGO:
        datasource.username = settings.MONGO_USERNAME
        datasource.password = settings.MONGO_PASSWORD
        datasource.name = settings.MONGO_DATABASE
        datasource.host = settings.MONGO_HOST
        datasource.port = settings.MONGO_PORT
        return datasource
    elif settings.STORAGE_ENGINE == MYSQL:
        datasource.username = settings.MYSQL_USER
        datasource.password = settings.MYSQL_PASSWORD
        datasource.name = settings.MYSQL_DATABASE
        datasource.host = settings.MYSQL_HOST
        datasource.port = settings.MYSQL_PORT
        return datasource
    elif settings.STORAGE_ENGINE == ORACLE:
        pass


def find_template():
    if settings.STORAGE_ENGINE == MONGO:
        from watchmen.database.mongo.mongo_template import MongoStorage
        default_datasource = get_default_datasource()
        engine  = MongoEngine(default_datasource)
        return MongoStorage(engine.get_engine())
    elif settings.STORAGE_ENGINE == MYSQL:
        from watchmen.database.mysql.mysql_template import MysqlStorage
        default_datasource = get_default_datasource()
        engine = MysqlEngine(default_datasource)
        return MysqlStorage(engine.get_engine())
    elif settings.STORAGE_ENGINE == ORACLE:
        from watchmen.database.oracle.oracle_template import OracleStorage
        return OracleStorage()
