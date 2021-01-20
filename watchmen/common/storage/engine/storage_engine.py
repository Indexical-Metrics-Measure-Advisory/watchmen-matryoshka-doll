from pymongo import MongoClient

from watchmen.config.config import settings

client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)


def get_client(name):
    return client[name]



