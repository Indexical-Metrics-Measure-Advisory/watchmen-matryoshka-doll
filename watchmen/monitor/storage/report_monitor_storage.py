from watchmen.common.storage.engine.storage_engine import get_monitor_db

db = get_monitor_db()
monitor_pipeline_collection = db.get_collection('monitor_report')


def insert_report_monitor(report_status):
    monitor_pipeline_collection.insert_one(report_status.dict())
