from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN

db = get_client(WATCHMEN)


def batch_import_data(data_list, name):
    collection = db.get_collection(name)
    return collection.insert_many(data_list)




