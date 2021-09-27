from watchmen.common.constants import pipeline_constants
from watchmen.common.utils.data_utils import is_raw
from watchmen.database.storage.utils.topic_utils import get_flatten_field
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.utils.units_func import INSERT, add_audit_columns
from watchmen.topic.storage.topic_data_storage import save_topic_instance


async def import_raw_topic_data(topic,topic_event, current_user):
    data = get_input_data(topic, topic_event)
    add_audit_columns(data, INSERT)
    if is_raw(topic):
        flatten_fields = get_flatten_field(topic_event.data, topic.factors)
        data.update(flatten_fields)

    save_topic_instance(topic, data,current_user)
    trigger_pipeline(topic_event.code, {pipeline_constants.NEW: topic_event.data, pipeline_constants.OLD: None},
                     TriggerType.insert, current_user)


async def run_pipeline_from_raw_data(topic ,data, current_user):
    add_audit_columns(data, INSERT)
    pass



async def run_pipeline_from_topic_data(topic,data,current_user):

    pass


def get_input_data(topic, topic_event):
    if is_raw(topic):
        data = {"data_": topic_event.data}
    else:
        data = topic_event.data
    return data