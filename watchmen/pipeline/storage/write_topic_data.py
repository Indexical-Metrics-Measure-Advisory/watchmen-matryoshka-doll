import logging
from typing import List

from model.model.pipeline.trigger_data import TriggerData
from model.model.pipeline.trigger_type import TriggerType
from model.model.topic.factor import Factor
from model.model.topic.topic import Topic

from watchmen.common.constants import pipeline_constants
from watchmen.common.utils.data_utils import get_id_name_by_datasource, add_tenant_id_to_instance
from watchmen_boot.config.config import settings
from watchmen.database.datasource.container import data_source_container
from watchmen.database.topic.adapter.topic_storage_adapter import get_template_by_datasource_id
from watchmen.pipeline.utils.units_func import add_audit_columns, add_trace_columns, INSERT, UPDATE
from watchmen.security.index import encrypt_value

log = logging.getLogger("app." + __name__)


def __build_trigger_pipeline_data(topic_name: str, data, trigger_type):
    return TriggerData(topicName=topic_name, triggerType=trigger_type, data=data)


def __find_encrypt_factor_in_mapping_result(mapping_result, topic: Topic) -> List[Factor]:
    need_encrypt_factors = list(
        filter(lambda factor: factor.name in mapping_result and factor.encrypt is not None, topic.factors))
    return need_encrypt_factors


def __need_encrypt():
    return settings.DATA_SECURITY_ON


def __encrypt_value(need_encrypt_factors: List[Factor], mapping_result, current_user):
    for factor in need_encrypt_factors:
        if __need_encrypt():
            value_after_encrypt = encrypt_value(factor.type, factor.encrypt, mapping_result[factor.name],
                                                current_user.tenantId)
            log.info("factor name {0} encrypt_value is {1}".format(factor.name, value_after_encrypt))
            mapping_result[factor.name] = value_after_encrypt


def insert_topic_data(mapping_result, pipeline_uid, topic: Topic, current_user):
    if current_user is None:
        raise Exception("current_user is None")
    add_audit_columns(mapping_result, INSERT)
    add_tenant_id_to_instance(mapping_result, current_user)
    add_trace_columns(mapping_result, "insert_row", pipeline_uid)
    if __need_encrypt():
        __encrypt_value(__find_encrypt_factor_in_mapping_result(mapping_result, topic), mapping_result, current_user)
    template = get_template_by_datasource_id(topic.dataSourceId)
    template.topic_data_insert_one(mapping_result, topic.name)
    return __build_trigger_pipeline_data(topic.name,
                                         {pipeline_constants.NEW: mapping_result, pipeline_constants.OLD: None},
                                         TriggerType.insert)


def update_topic_data(mapping_result, target_data, pipeline_uid, query_, topic: Topic, current_user):
    if current_user is None:
        raise Exception("current_user is None")
    template = get_template_by_datasource_id(topic.dataSourceId)
    old_data = template.topic_data_find_by_id(
        target_data[get_id_name_by_datasource(data_source_container.get_data_source_by_id(topic.dataSourceId))],
        topic.name)
    add_audit_columns(mapping_result, UPDATE)
    add_tenant_id_to_instance(mapping_result, current_user)
    if __need_encrypt():
        __encrypt_value(__find_encrypt_factor_in_mapping_result(mapping_result, topic), mapping_result, current_user)
    add_trace_columns(mapping_result, "update_row", pipeline_uid)
    template.topic_data_update_(query_, mapping_result, topic.name)
    data = {**target_data, **mapping_result}
    return __build_trigger_pipeline_data(topic.name,
                                         {pipeline_constants.NEW: data, pipeline_constants.OLD: old_data},
                                         TriggerType.update)


def update_topic_data_one(mapping_result, target_data, pipeline_uid, id_, topic: Topic, current_user):
    if current_user is None:
        raise Exception("current_user is None")
    template = get_template_by_datasource_id(topic.dataSourceId)
    old_data = template.topic_data_find_by_id(
        target_data[get_id_name_by_datasource(data_source_container.get_data_source_by_id(topic.dataSourceId))],
        topic.name)
    add_audit_columns(mapping_result, UPDATE)
    add_trace_columns(mapping_result, "update_row", pipeline_uid)
    if __need_encrypt():
        __encrypt_value(__find_encrypt_factor_in_mapping_result(mapping_result, topic), mapping_result, current_user)
    add_tenant_id_to_instance(mapping_result, current_user)
    template.topic_data_update_one(id_, mapping_result, topic.name)
    data = {**target_data, **mapping_result}
    return __build_trigger_pipeline_data(topic.name,
                                         {pipeline_constants.NEW: data, pipeline_constants.OLD: old_data},
                                         TriggerType.update)


def update_topic_data_one_with_version(mapping_result, target_data, pipeline_uid, id_, version_, topic: Topic,
                                       current_user):
    if current_user is None:
        raise Exception("current_user is None")
    template = get_template_by_datasource_id(topic.dataSourceId)
    old_data = template.topic_data_find_by_id(
        target_data[get_id_name_by_datasource(data_source_container.get_data_source_by_id(topic.dataSourceId))],
        topic.name)
    add_audit_columns(mapping_result, UPDATE)
    add_tenant_id_to_instance(mapping_result, current_user)
    add_trace_columns(mapping_result, "update_row", pipeline_uid)
    if __need_encrypt():
        __encrypt_value(__find_encrypt_factor_in_mapping_result(mapping_result, topic), mapping_result, current_user)
    template.topic_data_update_one_with_version(id_, version_, mapping_result, topic.name)
    data = {**target_data, **mapping_result}
    return __build_trigger_pipeline_data(topic.name,
                                         {pipeline_constants.NEW: data, pipeline_constants.OLD: old_data},
                                         TriggerType.update)
