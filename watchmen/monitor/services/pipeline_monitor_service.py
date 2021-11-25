from typing import List

from model.model.pipeline.trigger_type import TriggerType
from model.model.topic.factor import Factor
from model.model.topic.topic import Topic

import watchmen.pipeline.index
from watchmen.common.constants import pipeline_constants
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.database.topic.adapter.topic_storage_adapter import get_template_by_datasource_id
from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus
from watchmen.pipeline.core.parameter.utils import check_and_convert_value_by_factor
from watchmen.pipeline.utils.units_func import add_audit_columns, INSERT
from watchmen.topic.storage.topic_schema_storage import get_topic_by_name, save_topic


def sync_pipeline_monitor_data(pipeline_monitor: PipelineRunStatus):
    code = "raw_pipeline_monitor"
    data = pipeline_monitor.dict()
    raw_data = {"data_": data, "tenant_id_": pipeline_monitor.tenantId, "traceid": pipeline_monitor.traceId}
    topic = find_monitor_topic(code, pipeline_monitor.currentUser)
    trace_id = get_surrogate_key()
    if topic is None:
        raise Exception(code + " topic name does not exist")
    add_audit_columns(raw_data, INSERT)
    flatten_fields = get_flatten_field(data, topic.factors)
    raw_data.update(flatten_fields)
    storage_template = get_template_by_datasource_id(topic.dataSourceId)
    storage_template.topic_data_insert_one(raw_data, code)
    watchmen.pipeline.index.trigger_pipeline(code,
                                             {pipeline_constants.NEW: data, pipeline_constants.OLD: None},
                                             TriggerType.insert,
                                             pipeline_monitor.currentUser, trace_id)


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


def find_monitor_topic(topic_name, current_user):
    topic = get_topic_by_name(topic_name, current_user)
    if topic is None:
        return get_topic_by_name(topic_name)
    else:
        return topic
