import json

from bson import ObjectId as BsonObjectId
import decamelize

from watchmen.entity.data_entity import DataEntity
from watchmen.entity.data_entity_set import DataEntitySet
from watchmen.entity.data_relationship import DataRelationship
from watchmen.schema.model_schema import ModelSchema
from watchmen.schema.model_schema_set import ModelSchemaSet
from watchmen.utils.data_utils import get_dict_schema_set, get_dict_relationship, is_field_value


class Event(object):
    code: str
    type: str


def process_topic_data():
    # TODO topic match
    pass


def process_model(sub, schema: ModelSchema, entity_set: DataEntitySet, relationship_dict,schema_dict,data_relationship):
    entity = DataEntity()
    entity.entityId=str(BsonObjectId())
    data_relationship.childId=entity.entityId
    entity.name=data_relationship.name
    entity.topicCode = schema.name
    for key, value in sub.items():
        if is_field_value(value):
            process_data_attr(schema, key, value, entity)
        else:
            relationships = relationship_dict[schema.modelId]
            for relationship in relationships:
                if key == relationship.name:
                    sub_schema = schema_dict[relationship.childId]
            for sub in value:
                process_model(sub, sub_schema, entity_set,relationship_dict,schema_dict,data_relationship)

    entity_set.relationships.append(data_relationship)
    entity_set.entities.append(entity)
    # return entity


def process_data_attr(schema, key, value, entity):
    field_schema = schema.businessFields[key]
    # TODO[next]  validation rule for value
    entity.attr[key] = value


def find_root_schema(schema_dict: dict):
    # TODO mock data
    return schema_dict["5f59deae3d9beb556e1d302d"]


def generate_description(name):
    # print( decamelize.convert(name))
    return decamelize.convert(name)


def import_row_data(data: json, schema_set: ModelSchemaSet, event: Event):
    schema_dict = get_dict_schema_set(schema_set)
    relationship_dict = get_dict_relationship(schema_set)
    schema = find_root_schema(schema_dict)
    entity_set = DataEntitySet()
    entity = DataEntity()
    entity.topicCode= schema.name

    entity.entityId = str(BsonObjectId())
    for key, value in data.items():
        if is_field_value(value):
            process_data_attr(schema, key, value, entity)
        else:
            relationships = relationship_dict[schema.modelId]
            for relationship in relationships:
                if key == relationship.name:
                    sub_schema = schema_dict[relationship.childId]
                    for sub in value:
                        data_relationship = DataRelationship()
                        data_relationship.parentId = entity.entityId
                        data_relationship.type = relationship.type
                        data_relationship.name = relationship.name
                        data_relationship.desc = generate_description(relationship.name)
                        process_model(sub, sub_schema, entity_set, relationship_dict, schema_dict, data_relationship)

            # TODO[next] one to one default merge to main topic


    entity_set.entities.append(entity)
    print(entity_set.json())
    return entity_set

    # find sub schema in relationship schema
    # process attr
    # generate ID   for sub schema`s relationship


def batch_import_data():
    # find schema

    # extract data topic base on schema

    # TODO[future] use dark for parallel run
    pass
