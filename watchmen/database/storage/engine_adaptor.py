from watchmen.config.config import settings


MYSQL = "mysql"
MONGO = "mongo"
ORACLE = "oracle"


def find_template():
    # print(settings.STORAGE_ENGINE)
    if settings.STORAGE_ENGINE == MONGO:
        # from watchmen.database.mongo import mongo_template
        # return mongo_template
        from watchmen.database.mongo.mongo_template import MongoStorage
        return MongoStorage()

    elif settings.STORAGE_ENGINE == MYSQL:
        # from watchmen.database.mysql import mysql_template
        # return mysql_template
        from watchmen.database.mysql.mysql_template import MysqlStorage
        return MysqlStorage()
    elif settings.STORAGE_ENGINE == ORACLE:
        from watchmen.database.oracle.oracle_template import OracleStorage
        return OracleStorage()
