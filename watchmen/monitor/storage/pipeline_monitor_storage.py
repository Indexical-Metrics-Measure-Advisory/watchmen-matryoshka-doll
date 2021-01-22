# from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN
from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus

db = get_client(WATCHMEN)
monitor_pipeline_collection = db.get_collection('monitor_pipeline')


def insert_pipeline_monitor(pipeline_status: PipelineRunStatus):
    monitor_pipeline_collection.insert_one(pipeline_status.dict())
