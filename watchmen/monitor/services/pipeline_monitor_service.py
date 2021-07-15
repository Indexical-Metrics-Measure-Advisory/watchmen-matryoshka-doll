
import watchmen.pipeline.index
from watchmen.collection.model.topic_event import TopicEvent
from watchmen.common.constants import pipeline_constants
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.database.storage.storage_template import topic_data_insert_one

from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.utils.units_func import add_audit_columns, INSERT
from watchmen.topic.storage.topic_schema_storage import get_topic, get_topic_by_name, save_topic
from watchmen.topic.topic import Topic


def sync_pipeline_monitor_data(pipeline_monitor: PipelineRunStatus):
    topic_event = TopicEvent(code="raw_pipeline_monitor", data=pipeline_monitor.dict())

    topic = get_topic(topic_event.code)
    if topic is None:
        raise Exception("topic name does not exist")

    add_audit_columns(topic_event.data, INSERT)
    raw_monitor_data = {"data_": topic_event.data, **topic_event.data}
    topic_data_insert_one(raw_monitor_data, topic_event.code)
    watchmen.pipeline.index.trigger_pipeline(topic_event.code,
                                             {pipeline_constants.NEW: topic_event.data, pipeline_constants.OLD: None},
                                             TriggerType.insert)


def insert_monitor_topic():
    monitor_topic = get_topic_by_name("raw_pipeline_monitor")
    if monitor_topic is None:
        topic = Topic()
        topic.topicId = get_surrogate_key()
        topic.name = "raw_pipeline_monitor"
        topic.type = "raw"
        topic.kind = "system"
        save_topic(topic)
