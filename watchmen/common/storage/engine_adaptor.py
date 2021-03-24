from watchmen.common.mongo import mongo_template
from watchmen.common.mysql import mysql_template
from watchmen.config.config import settings

MYSQL = "mysql"
MONGO = "mongo"
ORACLE = "oracle"


def find_template():
    if settings.STORAGE_ENGINE == MONGO:
        return mongo_template
    elif settings.STORAGE_ENGINE == MYSQL:
        return mysql_template
    elif settings.STORAGE_ENGINE == ORACLE:
        raise Exception("do not support Oracle")
