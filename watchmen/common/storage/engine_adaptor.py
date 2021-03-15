from watchmen.common.mongo import mongo_template
from watchmen.config.config import settings

MYSQL = "mysql"
MONGO = "mongo"


def find_template():
    if settings.STORAGE_ENGINE == MONGO:
        return mongo_template
    elif settings.STORAGE_ENGINE == MYSQL:
        raise Exception("do not support MySQL")
