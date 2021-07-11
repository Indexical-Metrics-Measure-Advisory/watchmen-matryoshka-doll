from watchmen.common.constants import pipeline_constants
from watchmen.common.utils.data_utils import get_id_name
from watchmen.database.storage.storage_template import topic_data_find_by_id, \
    topic_data_insert_one, topic_data_update_, topic_data_update_one
from watchmen.database.storage.storage_template import topic_data_update_one_with_version
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.model.trigger_data import TriggerData
from watchmen.pipeline.utils.units_func import add_audit_columns, add_trace_columns, INSERT, UPDATE


def __build_trigger_pipeline_data(topic_name: str, data, trigger_type):
    return TriggerData(topicName=topic_name, triggerType=trigger_type, data=data)


def insert_topic_data(topic_name, mapping_result, pipeline_uid):
    add_audit_columns(mapping_result, INSERT)
    add_trace_columns(mapping_result, "insert_row", pipeline_uid)
    topic_data_insert_one(mapping_result, topic_name)
    return __build_trigger_pipeline_data(topic_name,
                                         {pipeline_constants.NEW: mapping_result, pipeline_constants.OLD: None},
                                         TriggerType.insert)


def update_topic_data(topic_name, mapping_result, target_data, pipeline_uid, mongo_query):
    old_data = topic_data_find_by_id(target_data[get_id_name()], topic_name)
    add_audit_columns(mapping_result, UPDATE)
    add_trace_columns(mapping_result, "update_row", pipeline_uid)
    topic_data_update_(mongo_query, mapping_result, topic_name)
    data = {**target_data, **mapping_result}
    return __build_trigger_pipeline_data(topic_name,
                                         {pipeline_constants.NEW: data, pipeline_constants.OLD: old_data},
                                         TriggerType.update)


def update_topic_data_one(topic_name, mapping_result, target_data, pipeline_uid, id_):
    old_data = topic_data_find_by_id(target_data[get_id_name()], topic_name)
    add_audit_columns(mapping_result, UPDATE)
    add_trace_columns(mapping_result, "update_row", pipeline_uid)
    topic_data_update_one(id_, mapping_result, topic_name)
    data = {**target_data, **mapping_result}
    return __build_trigger_pipeline_data(topic_name,
                                         {pipeline_constants.NEW: data, pipeline_constants.OLD: old_data},
                                         TriggerType.update)


def update_topic_data_one_with_version(topic_name, mapping_result, target_data, pipeline_uid, id_, version_):
    old_data = topic_data_find_by_id(target_data[get_id_name()], topic_name)
    add_audit_columns(mapping_result, UPDATE)
    add_trace_columns(mapping_result, "update_row", pipeline_uid)
    topic_data_update_one_with_version(id_, version_, mapping_result, topic_name)
    data = {**target_data, **mapping_result}
    return __build_trigger_pipeline_data(topic_name,
                                         {pipeline_constants.NEW: data, pipeline_constants.OLD: old_data},
                                         TriggerType.update)

