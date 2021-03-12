from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name

client = get_client()

collection_list_name = client.list_collection_names()


def check_collection_if_exist(dbname, collection_name):
    return collection_name in collection_list_name


def delete_topic_collection(collection_name):
    topic_name = build_collection_name(collection_name)
    client.get_collection(topic_name).drop()

