from pymongo import MongoClient


# TODO load config data from file
client = MongoClient('localhost', 27017)


def get_client(name):
    return client[name]


