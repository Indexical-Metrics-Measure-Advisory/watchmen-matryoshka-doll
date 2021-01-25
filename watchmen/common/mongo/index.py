from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN

client = get_client()

collection_list_name = client.list_collection_names()


def check_collection_if_exist(dbname, collection_name):
    return collection_name in collection_list_name
