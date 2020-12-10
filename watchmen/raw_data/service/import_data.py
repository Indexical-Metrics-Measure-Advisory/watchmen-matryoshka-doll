import json

from bson import ObjectId as BsonObjectId
import decamelize

from watchmen.event.event import Event
from watchmen.raw_data.entity.data_entity import DataEntity
from watchmen.raw_data.entity.data_entity_set import DataEntitySet
from watchmen.raw_data.entity.data_relationship import DataRelationship
from watchmen.raw_data.model_schema import ModelSchema
from watchmen.raw_data.model_schema_set import ModelSchemaSet
from watchmen.raw_data.storage.row_data_storage import save_entity_set

from watchmen.utils.data_utils import get_dict_schema_set, get_dict_relationship, is_field_value


def process_topic_data():
    # TODO topic match
    pass


def process_raw_data(data: json, schema_set: ModelSchemaSet, event: Event):
    entity_set = import_raw_data(data, schema_set, event)
    print("------",entity_set.json())
    return save_entity_set(entity_set)


def process_model(sub, schema: ModelSchema, entity_set: DataEntitySet, relationship_dict, schema_dict,
                  data_relationship):
    entity = DataEntity()
    entity.entityId = str(BsonObjectId())
    data_relationship.childId = entity.entityId
    entity.name = data_relationship.name
    entity.topicCode = schema.name
    for key, value in sub.items():
        if is_field_value(value):
            process_data_attr(schema, key, value, entity)
        else:
            relationships = relationship_dict[schema.modelId]
            for relationship in relationships:
                if key == relationship.childName:
                    sub_schema = schema_dict[relationship.childId]
                    for sub in value:
                        data_relationship = build_data_relationship(entity, relationship)
                        process_model(sub, sub_schema, entity_set, relationship_dict, schema_dict, data_relationship)

    entity_set.relationships.append(data_relationship)
    entity_set.entities.append(entity)


def build_data_relationship(entity, relationship):
    data_relationship = DataRelationship()
    data_relationship.parentId = entity.entityId
    data_relationship.type = relationship.type
    data_relationship.name = relationship.name
    data_relationship.desc = generate_description(relationship.childName)
    return data_relationship


def process_data_attr(schema, key, value, entity):
    field_schema = schema.businessFields[key]
    # TODO[next]  validation rule for value
    entity.attr[key] = value


def find_root_schema(schema_dict: dict):
    for schema in schema_dict.values():
        if schema.isRoot is True:
            return schema

def generate_description(name):
    # print( decamelize.convert(name))
    return decamelize.convert(name)


def import_raw_data(data: json, schema_set: ModelSchemaSet, event: Event):
    schema_dict = get_dict_schema_set(schema_set)
    relationship_dict = get_dict_relationship(schema_set)
    schema = find_root_schema(schema_dict)
    entity_set = DataEntitySet()
    entity_set.event = event
    entity_set.domain = schema.name
    entity = DataEntity()
    entity.topicCode = schema.name

    entity.entityId = str(BsonObjectId())
    for key, value in data.items():
        if is_field_value(value):
            process_data_attr(schema, key, value, entity)
        else:

            relationships = relationship_dict[schema.modelId]
            for relationship in relationships:
                if key == relationship.childName:
                    sub_schema = schema_dict[relationship.childId]
                    for sub in value:
                        data_relationship = DataRelationship()
                        data_relationship.parentId = entity.entityId
                        data_relationship.type = relationship.type
                        data_relationship.name = relationship.name
                        data_relationship.desc = generate_description(relationship.childName)
                        process_model(sub, sub_schema, entity_set, relationship_dict, schema_dict, data_relationship)

            # TODO[next] one to one default merge to main topic

    entity_set.entities.append(entity)
    return entity_set

    # find sub raw_data in relationship raw_data
    # process attr
    # generate ID   for sub raw_data`s relationship


def batch_import_data():
    # find raw_data

    # extract data topic base on raw_data

    # TODO[future] use dark for parallel run
    pass
