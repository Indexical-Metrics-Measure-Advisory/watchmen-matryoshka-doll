from watchmen.common.storage.engine.storage_engine import get_monitor_db
from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus

db = get_monitor_db()
monitor_pipeline_collection = db.get_collection('monitor_pipeline')
monitor_unit_collection = db.get_collection('monitor_unit')


def insert_pipeline_monitor(pipeline_status: PipelineRunStatus):
    monitor_pipeline_collection.insert_one(pipeline_status.dict())

#
# def insert_stage_monitor(stage_status):
#     pass


def insert_units_monitor(unit_status_list):
    monitor_unit_collection.insert_many(unit_status_list)
