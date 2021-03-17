from watchmen.common.constants import pipeline_constants
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.single.stage.unit.utils.units_func import INSERT, add_audit_columns
from watchmen.topic.storage.topic_data_storage import save_topic_instance
from watchmen.topic.storage.topic_schema_storage import get_topic


#
#
# def crate_topic_by_raw_data_schema(schema, topic_list, mapping_list):
#     factor_list = []
#     node: schema
#     topic: Topic = Topic(**{'topic_id': get_surrogate_key(), 'name': '', 'topic_type': '', 'factors': []})
#     mapping: {}
#     # 遍历tree, 创建mapping和topic
#     node = schema
#     entity = node.data_entity
#
#     # 每个node上的data_entity对应一个topic，data_entity上的一个attr对应一个factor
#     topic.name = entity.name
#     topic.topic_type = 'test'
#     attr_list = entity.attrs
#     mapping = Mapping(**{
#         'mapping_id': get_surrogate_key(),
#         'source_entity_id': entity.entity_id,
#         'source_entity_name': entity.name,
#         'target_topic_id': topic.topicId,
#         'target_topic_name': entity.name,
#         'mapping_detail_list': []
#     })
#     mapping_detail_list = []
#     for attr in attr_list:
#         factor: Factor = Factor(**{'id': get_surrogate_key(), 'name': '', 'type': ''})
#         factor.name = attr.name
#         factor.type = attr.type
#         factor_list.append(factor)
#         mapping_detail = MappingDetail(**{'source_attr': attr, 'target_factor': factor})
#         mapping_detail_list.append(mapping_detail)
#
#     topic.factors = factor_list
#     topic_list.append(topic)
#     mapping.mapping_detail_list = mapping_detail_list
#     mapping_list.append(mapping)
#     if len(node.childs) == 0:
#         return
#     else:
#         for node in node.childs:
#             crate_topic_by_raw_data_schema(node, topic_list, mapping_list)
#     return mapping_list


async def import_raw_topic_data(topic_event):
    topic = get_topic(topic_event.code)
    if topic is None:
        raise Exception("topic name does not exist")

    add_audit_columns(topic_event.data, INSERT)
    save_topic_instance(topic_event.code, topic_event.data)
    await __trigger_pipeline(topic_event)


async def __trigger_pipeline(topic_event):
    trigger_pipeline(topic_event.code, {pipeline_constants.NEW: topic_event.data, pipeline_constants.OLD: None},
                     TriggerType.insert)
