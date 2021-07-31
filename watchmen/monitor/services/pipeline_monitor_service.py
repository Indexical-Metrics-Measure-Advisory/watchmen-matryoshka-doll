from typing import List

import watchmen.pipeline.index
from watchmen.common.constants import pipeline_constants
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.database.storage.storage_template import topic_data_insert_one

from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus
from watchmen.pipeline.core.parameter.utils import check_and_convert_value_by_factor
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.utils.units_func import add_audit_columns, INSERT
from watchmen.topic.factor.factor import Factor
from watchmen.topic.storage.topic_schema_storage import get_topic, get_topic_by_name, save_topic
from watchmen.topic.topic import Topic


'''
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
'''


def sync_pipeline_monitor_data(pipeline_monitor: PipelineRunStatus):
    code = "raw_pipeline_monitor"
    data = pipeline_monitor.dict()
    raw_data = {"data_": data}
    topic = get_topic(code)
    if topic is None:
        raise Exception(code + " topic name does not exist")
    add_audit_columns(raw_data, INSERT)
    flatten_fields = get_flatten_field(data, topic.factors)
    raw_data.update(flatten_fields)
    topic_data_insert_one(raw_data, code)
    watchmen.pipeline.index.trigger_pipeline(code,
                                             {pipeline_constants.NEW: data, pipeline_constants.OLD: None},
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


def get_flatten_field(data: dict, factors: List[Factor]):
    flatten_fields = {}
    for factor in factors:
        if factor.flatten:
            key = factor.name
            value = check_and_convert_value_by_factor(factor, data.get(key, None))
            flatten_fields[key.lower()] = value
    return flatten_fields