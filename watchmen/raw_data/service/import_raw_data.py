from watchmen.common.constants import pipeline_constants
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.single.stage.unit.utils.units_func import INSERT, add_audit_columns
from watchmen.topic.storage.topic_data_storage import save_topic_instance
from watchmen.topic.storage.topic_schema_storage import get_topic


async def import_raw_topic_data(topic_event):
    topic = get_topic(topic_event.code)
    if topic is None:
        raise Exception(topic_event.code + " topic name does not exist")

    add_audit_columns(topic_event.data, INSERT)
    save_topic_instance(topic_event.code, topic_event.data)

    # client = get_dask_client()
    # task = client.submit(__trigger_pipeline, topic_event)
    # # import_raw_topic_data(topic_event)
    # fire_and_forget(task)
    __trigger_pipeline(topic_event)


def __trigger_pipeline(topic_event):
    trigger_pipeline(topic_event.code, {pipeline_constants.NEW: topic_event.data, pipeline_constants.OLD: None},
                     TriggerType.insert)
