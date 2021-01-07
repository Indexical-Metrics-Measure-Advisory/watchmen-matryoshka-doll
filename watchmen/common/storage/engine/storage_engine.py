from pymongo import MongoClient

from watchmen.config.config import settings

# TODO load config data from file
client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)


def get_client(name):
    return client[name]
