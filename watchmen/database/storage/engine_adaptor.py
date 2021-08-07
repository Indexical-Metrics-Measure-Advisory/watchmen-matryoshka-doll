from watchmen.config.config import settings

MYSQL = "mysql"
MONGO = "mongo"
ORACLE = "oracle"


def find_template():
    if settings.STORAGE_ENGINE == MONGO:
        from watchmen.database.mongo.mongo_template import MongoStorage
        return MongoStorage()
    elif settings.STORAGE_ENGINE == MYSQL:
        from watchmen.database.mysql.mysql_template import MysqlStorage
        return MysqlStorage()
    elif settings.STORAGE_ENGINE == ORACLE:
        from watchmen.database.oracle.oracle_template import OracleStorage
        return OracleStorage()
