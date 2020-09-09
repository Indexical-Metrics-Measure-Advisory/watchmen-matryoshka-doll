import json

from watchmen.entity.data_entity import DataEntity
from watchmen.entity.data_entity_set import DataEntitySet
from watchmen.schema.model_schema_set import ModelSchemaSet
from watchmen.utils.data_utils import get_dict_schema_set, get_dict_relationship, is_field_value


class Event(object):
    code: str
    type: str


def process_topic_data():
    pass


def process_data_attr(schema, key, value, entity):
    field_schema = schema.businessFields[key]
    # TODO[M] value validation rule
    entity.attr[key] = value


def find_root_schema(schema_dict: dict):
    return schema_dict["5f589b973d9beb32a4a92f38"]


def import_row_data(data: json, schema_set: ModelSchemaSet, event: Event):
    schema_dict = get_dict_schema_set(schema_set)
    relationship_dict = get_dict_relationship(schema_set)
    schema = find_root_schema(schema_dict)
    entity_set = DataEntitySet()
    entity = DataEntity()
    for key, value in data.items():
        if is_field_value(value):
            process_data_attr(schema, key, value, entity)
        else:
            relationships = relationship_dict[schema.modelId]
            for relationship in relationships:
                if key == relationship.name:
                    sub_schema = schema_dict[relationship.childId]

    entity_set.entities.append(entity)
    return entity_set

    # find sub schema in relationship schema
    # process attr
    # generate ID   for sub schema`s relationship


def batch_import_data():
    # find schema

    # extract data topic base on schema

    # TODO[future] use dark for parallel run
    pass
