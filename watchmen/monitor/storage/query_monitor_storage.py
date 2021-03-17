from watchmen.common.storage.engine.storage_engine import get_monitor_db

db = get_monitor_db()

query_monitor_collections = db.get_collection("monitor_query")


def insert_query_monitor(query_monitor):
    query_monitor_collections.insert_one(query_monitor.dict())
