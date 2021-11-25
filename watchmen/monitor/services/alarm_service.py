import asyncio

from watchmen.collection.model.topic_event import TopicEvent
from model.model.common.alarm import AlarmMessage
from watchmen.common.constants import pipeline_constants
from watchmen.common.notify.notify_service import send_notifier
from watchmen.pipeline.index import trigger_pipeline
from model.model.pipeline.trigger_type import TriggerType
from watchmen.pipeline.utils.units_func import add_audit_columns, INSERT
from watchmen.topic.storage.topic_data_storage import save_topic_instance
from watchmen.topic.storage.topic_schema_storage import get_topic


def sync_alarm_message(alarm: AlarmMessage):
    topic_event = TopicEvent(code="alarm", data=alarm.dict())
    topic = get_topic(topic_event.code)
    if topic is None:
        raise Exception("topic name does not exist")
    add_audit_columns(topic_event.data, INSERT)
    save_topic_instance(topic_event.code, topic_event.data)
    trigger_pipeline(topic_event.code,
                     {pipeline_constants.NEW: topic_event.data, pipeline_constants.OLD: None},
                     TriggerType.insert)
    asyncio.ensure_future(send_notifier(alarm))
