from watchmen.common.constants import pipeline_constants
from watchmen.common.utils.data_utils import is_raw
from watchmen.database.topic_utils import get_flatten_field
from watchmen.pipeline.index import trigger_pipeline
from model.model.pipeline.trigger_type import TriggerType
from watchmen.pipeline.utils.units_func import INSERT, add_audit_columns
from watchmen.topic.storage.topic_data_storage import save_topic_instance


async def save_topic_data(topic, data, current_user):
    add_audit_columns(data, INSERT)
    if is_raw(topic):
        flatten_fields = get_flatten_field(data["data_"], topic.factors)
        data.update(flatten_fields)

    save_topic_instance(topic, data, current_user)


def get_input_data(topic, topic_event):
    if is_raw(topic):
        raw_data = {"data_": topic_event.data}
    else:
        raw_data = topic_event.data
    return raw_data


async def run_pipeline(topic_event, current_user, trace_id=None):
    trigger_pipeline(topic_event.code, {pipeline_constants.NEW: topic_event.data, pipeline_constants.OLD: None},
                     TriggerType.insert, current_user, trace_id)
