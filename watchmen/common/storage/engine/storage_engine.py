from pymongo import MongoClient

from watchmen.common.utils.data_utils import WATCHMEN
from watchmen.config.config import settings

client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)

db = client[WATCHMEN]


def get_client():
    return db


def get_client_db():
    return client
