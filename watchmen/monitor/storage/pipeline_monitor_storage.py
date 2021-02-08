from watchmen.common.storage.engine.storage_engine import get_monitor_db
from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus

db = get_monitor_db()
monitor_pipeline_collection = db.get_collection('monitor_pipeline')


def insert_pipeline_monitor(pipeline_status: PipelineRunStatus):
    monitor_pipeline_collection.insert_one(pipeline_status.dict())


def insert_stage_monitor(stage_status):
    pass
