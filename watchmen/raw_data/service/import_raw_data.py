import json

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.raw_data.mapping import Mapping, MappingDetail
from watchmen.topic.factor.factor import Factor
from watchmen.topic.topic import Topic


def create_raw_data_schema(domain_code, data: json):
    pass


def import_raw_data(domain_code, data: json, is_create_schema):
    pass
    # TODO[next] one to one default merge to main topic
    # find sub raw_data_back in relationship raw_data_back
    # process attr
    # generate ID   for sub raw_data_back`s relationship


def mapping_raw_data(raw_data, mapping_list):
    pass


## TODO remove
def crate_topic_by_raw_data_schema(schema, topic_list, mapping_list):
    factor_list = []
    node: schema
    topic: Topic = Topic(**{'topic_id': get_surrogate_key(), 'name': '', 'topic_type': '', 'factors': []})
    mapping: {}
    # 遍历tree, 创建mapping和topic
    node = schema
    entity = node.data_entity

    # 每个node上的data_entity对应一个topic，data_entity上的一个attr对应一个factor
    topic.name = entity.name
    topic.topic_type = 'test'
    attr_list = entity.attrs
    mapping = Mapping(**{
        'mapping_id': get_surrogate_key(),
        'source_entity_id': entity.entity_id,
        'source_entity_name': entity.name,
        'target_topic_id': topic.topicId,
        'target_topic_name': entity.name,
        'mapping_detail_list': []
    })
    mapping_detail_list = []
    for attr in attr_list:
        factor: Factor = Factor(**{'id': get_surrogate_key(), 'name': '', 'type': ''})
        factor.name = attr.name
        factor.type = attr.type
        factor_list.append(factor)
        mapping_detail = MappingDetail(**{'source_attr': attr, 'target_factor': factor})
        mapping_detail_list.append(mapping_detail)

    topic.factors = factor_list
    topic_list.append(topic)
    mapping.mapping_detail_list = mapping_detail_list
    mapping_list.append(mapping)
    if len(node.childs) == 0:
        return
    else:
        for node in node.childs:
            crate_topic_by_raw_data_schema(node, topic_list, mapping_list)
    return mapping_list


def batch_import_data(domain_code, data):
    # find schema

    # extract data topic base on raw_data_back

    # TODO[future] use dark for parallel run
    pass
