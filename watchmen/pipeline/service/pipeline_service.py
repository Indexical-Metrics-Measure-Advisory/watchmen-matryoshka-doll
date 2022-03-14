from model.model.pipeline.trigger_type import TriggerType

from watchmen.common.constants import pipeline_constants
from watchmen.common.utils.data_utils import is_raw
from watchmen.database.topic_utils import get_flatten_field
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.utils.units_func import INSERT, add_audit_columns, convert_datetime, DATETIME, FULL_DATETIME
from watchmen.topic.storage.topic_data_storage import save_topic_instance


async def save_topic_data(topic, data, current_user):
    add_audit_columns(data, INSERT)
    if is_raw(topic):
        flatten_fields = get_flatten_field(data["data_"], topic.factors)
        data.update(flatten_fields)
    else:
        data = process_factor_format(topic,data)

    save_topic_instance(topic, data, current_user)


def process_factor_format(topic,data):
    datetime_factors = get_datetime_factors(topic)
    for factor in datetime_factors:
        if factor.name in data:
            data[factor.name] = convert_datetime(data[factor.name])
    return data


def get_datetime_factors(topic):
    datetime_factors = []
    for factor in topic.factors:
        if factor.type == DATETIME or factor.type == FULL_DATETIME:
            datetime_factors.append(factor)

    return datetime_factors



def get_input_data(topic, topic_event):
    if is_raw(topic):
        raw_data = {"data_": topic_event.data}
    else:
        raw_data = topic_event.data
    return raw_data


async def run_pipeline(topic_event, current_user, trace_id=None):
    trigger_pipeline(topic_event.code, {pipeline_constants.NEW: topic_event.data, pipeline_constants.OLD: None},
                     TriggerType.insert, current_user, trace_id)
