from watchmen.config.config import settings
from watchmen.database.datasource.data_source import DataSource
from watchmen.database.mongo.mongo_client import MongoEngine

from watchmen.database.mysql.mysql_client import MysqlEngine

from watchmen.database.oracle.oracle_client import OracleEngine
from watchmen.database.table import mysql_table_definition, oracle_table_definition
from watchmen.database.table.base_table_definition import TableDefinition
from watchmen.database.table.mysql_table_definition import MysqlTableDefinition

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
        datasource.dataSourceType = "mongodb"
        return datasource
    elif settings.STORAGE_ENGINE == MYSQL:
        datasource.username = settings.MYSQL_USER
        datasource.password = settings.MYSQL_PASSWORD
        datasource.name = settings.MYSQL_DATABASE
        datasource.host = settings.MYSQL_HOST
        datasource.port = settings.MYSQL_PORT
        datasource.dataSourceType = "mysql"
        return datasource
    elif settings.STORAGE_ENGINE == ORACLE:
        datasource.username = settings.ORACLE_USER
        datasource.password = settings.ORACLE_PASSWORD
        datasource.name = settings.ORACLE_SERVICE
        datasource.host = settings.ORACLE_HOST
        datasource.port = settings.ORACLE_PORT
        datasource.dataSourceType = "oracle"
        return datasource


def find_template():
    default_datasource = get_default_datasource()
    if settings.STORAGE_ENGINE == MONGO:
        from watchmen.database.mongo.mongo_template import MongoStorage
        engine = MongoEngine(default_datasource)
        return MongoStorage(engine.get_engine(),TableDefinition())
    elif settings.STORAGE_ENGINE == MYSQL:
        from watchmen.database.mysql.mysql_template import MysqlStorage
        engine = MysqlEngine(default_datasource)
        return MysqlStorage(engine.get_engine(), MysqlTableDefinition())
    elif settings.STORAGE_ENGINE == ORACLE:
        from watchmen.database.oracle.oracle_template import OracleStorage
        engine = OracleEngine(default_datasource)
        return OracleStorage(engine.get_engine(), oracle_table_definition)
