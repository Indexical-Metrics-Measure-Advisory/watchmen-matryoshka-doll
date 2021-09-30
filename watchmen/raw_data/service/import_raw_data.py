from typing import List

from watchmen.common.constants import pipeline_constants
from watchmen.common.utils.data_utils import is_raw
from watchmen.pipeline.core.parameter.utils import check_and_convert_value_by_factor
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.utils.units_func import INSERT, add_audit_columns
from watchmen.topic.factor.factor import Factor
from watchmen.topic.storage.topic_data_storage import save_topic_instance
from watchmen.topic.storage.topic_schema_storage import get_topic


async def import_raw_topic_data(topic_event, current_user):

    print(topic_event.code)
    topic = get_topic(topic_event.code, current_user)
    if topic is None:
        raise Exception(topic_event.code + " topic name does not exist")
    # todo
    '''
    if not isinstance(topic_event.data, dict):
        raise ValueError("topic_event data should be dict, now it is {0}".format(topic_event.data))
    '''
    raw_data = await get_input_data(topic, topic_event)
    add_audit_columns(raw_data, INSERT)
    flatten_fields = get_flatten_field(topic_event.data, topic.factors)
    raw_data.update(flatten_fields)

    save_topic_instance(topic, raw_data,current_user)
    __trigger_pipeline(topic_event, current_user)


async def get_input_data(topic, topic_event):
    if is_raw(topic):
        raw_data = {"data_": topic_event.data}
    else:
        raw_data = topic_event.data
    return raw_data


def __trigger_pipeline(topic_event, current_user):
    trigger_pipeline(topic_event.code, {pipeline_constants.NEW: topic_event.data, pipeline_constants.OLD: None},
                     TriggerType.insert, current_user)


def get_flatten_field(data: dict, factors: List[Factor]):
    flatten_fields = {}
    for factor in factors:
        if factor.flatten:
            key = factor.name
            value = check_and_convert_value_by_factor(factor, data.get(key, None))
            flatten_fields[key.lower()] = value
    return flatten_fields
