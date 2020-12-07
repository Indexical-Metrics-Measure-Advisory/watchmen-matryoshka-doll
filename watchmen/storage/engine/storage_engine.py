from pymongo import MongoClient


# TODO load config data from file
client = MongoClient('localhost', 27017)


def get_client(name):
    return client[name]


def insert_data_by_schema(topic_name, data):
    mappings=get_mappings_by_topic(topic_name)
    master_data={}
    for mapping in mappings:
        field= mapping['source']
        type= mapping['type']
        master_data[field]= data[field]
    save_master_data(master_data)

def save_master_data(master_data):
    pass


def get_mappings_by_topic(topic_name):
    return [{}]