from watchmen.config.config import settings


MYSQL = "mysql"
MONGO = "mongo"
ORACLE = "oracle"


def find_template():
    # print(settings.STORAGE_ENGINE)
    if settings.STORAGE_ENGINE == MONGO:
        from watchmen.database.mongo import mongo_template
        return mongo_template
    elif settings.STORAGE_ENGINE == MYSQL:
        from watchmen.database.mysql import mysql_template
        return mysql_template
    elif settings.STORAGE_ENGINE == ORACLE:
        from watchmen.database.oracle import oracle_template
        return oracle_template
