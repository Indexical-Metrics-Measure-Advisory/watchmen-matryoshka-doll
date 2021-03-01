from pymongo import MongoClient

from watchmen.common.utils.data_utils import WATCHMEN, MONITOR
from watchmen.config.config import settings

client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT, username=settings.MONGO_USERNAME,
                     password=settings.MONGO_PASSWORD)

monitor_client = MongoClient(settings.MONGO_MONITOR_HOST, settings.MONGO_MONITOR_PORT,
                             username=settings.MONGO_MONITOR_USERNAME, password=settings.MONGO_MONITOR_PASSWORD)

db = client[WATCHMEN]

#   TODO adapter relationship db


def get_client():
    return db


def get_client_db():
    return client


def get_monitor_db():
    return monitor_client[MONITOR]
