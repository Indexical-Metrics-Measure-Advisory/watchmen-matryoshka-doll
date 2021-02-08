import logging

from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name

db = get_client()

collection = db.get_collection('_schema')

log = logging.getLogger("app." + __name__)


def remove_presto_schema_by_name(topic_name):
    try:
        collection.delete_one({"table":build_collection_name(topic_name)})
    except Exception as e:
        log.exception(e)
