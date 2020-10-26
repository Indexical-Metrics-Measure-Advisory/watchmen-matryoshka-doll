# import json
#
# from watchmen.lake.generate.model_schema_generater import generate_basic_schema
# from watchmen.lake.model_schema import Domain
#
#
# def generate_schema(key: str, data: json, domain: Domain):
#
#     return generate_basic_schema(key, data, domain)


import json

from bson import ObjectId as BsonObjectId, ObjectId

from watchmen.lake.model_field import ModelField, FieldType
from watchmen.lake.model_relationship import ModelRelationship, RelationshipType
from watchmen.lake.model_schema import ModelSchema, Domain
from watchmen.lake.model_schema_set import ModelSchemaSet
from watchmen.utils.data_utils import is_field_value

ROOT = "root"


def convert_value(value):
    if type(value) == ObjectId:
        value = str(value)
    return value


def __build_model_fields(key: str, value):
    model_field = ModelField()
    if type(value) == int or type(value) == float:
        model_field.name = key
        model_field.type = FieldType.NUM
    if type(value) == str:
        model_field.name = key
        model_field.type = FieldType.STR

    model_field.value.append(convert_value(value))
    return model_field


def __generate_sub_model(key: str, sub_model: json, sub_model_schema: ModelSchema, model_schema_set):
    sub_model_schema.name = key  # TODO[next] add logic for key check (same as topic match)
    process_attrs(sub_model, sub_model_schema, model_schema_set)
    # sub_model_schema.lexiconMatch = lexicon_match(sub_model_schema)
    return sub_model_schema


def __generate_schema(key: str, data: json, domain: Domain):
    model_schema = build_root_basic_info(domain, key)
    model_schema_set = ModelSchemaSet()
    process_attrs(data, model_schema, model_schema_set)
    # TODO value content match

    model_schema_set.schemas[model_schema.name] = model_schema

    return model_schema_set


def build_root_basic_info(domain, key):
    model_schema = ModelSchema()
    model_schema.modelId = str(BsonObjectId())
    model_schema.isRoot = True
    if key is None:
        model_schema.name = ROOT
    else:
        model_schema.name = key
    model_schema.domain = domain
    return model_schema


def __is_dict(value):
    return type(value) == dict or type(value) == list


def __get_type(value):
    if __is_dict(value):
        return RelationshipType.OneToMany
    else:
        return RelationshipType.OneToOne


def __build_relationship_key(relationship):
    return relationship.parentName + "-" + relationship.type.value + "-" + relationship.childName


def __build_sub_model_schema(model_schema_set, relationship_key):
    if relationship_key in model_schema_set.relationships:
        relationship = model_schema_set.relationships[relationship_key]
        return model_schema_set.schemas[relationship.childName]
    else:
        sub_model_schema = ModelSchema()
        sub_model_schema.modelId = str(BsonObjectId())
        return sub_model_schema


def process_attrs(data, model_schema, model_schema_set):
    # TODO identify ID attr
    for key, value in data.items():
        if is_field_value(value):

            # print (key in model_schema.businessFields)
            if key in model_schema.businessFields:
                model_schema.businessFields[key].value.append(convert_value(value))
            else:
                model_field = __build_model_fields(key, value)
                model_schema.businessFields[key] = model_field
        else:

            # if  model_schema_set.relationships

            # process sub lake
            sub_model_id = str(BsonObjectId())
            relationship = ModelRelationship()
            relationship.parentId = model_schema.modelId
            relationship.childId = sub_model_id
            relationship.parentName = model_schema.name
            relationship.childName = key
            relationship.type = __get_type(value)
            relationship_key = __build_relationship_key(relationship)

            sub_model_schema = __build_sub_model_schema(model_schema_set, relationship_key)
            if __is_dict(value):
                for sub_model in value:
                    sub_model_schema = __generate_sub_model(key, sub_model, sub_model_schema, model_schema_set)
            else:
                sub_model_schema = __generate_sub_model(key, value, sub_model_schema, model_schema_set)

            model_schema_set.schemas[sub_model_schema.name] = sub_model_schema
            model_schema_set.relationships[relationship_key] = relationship


def __create_links():
    pass


def generate_basic_schema_for_list_data(key: str, data_list: [], domain: Domain):
    model_schema = build_root_basic_info(domain, key)
    model_schema_set = ModelSchemaSet()
    for data in data_list:
        process_attrs(data, model_schema, model_schema_set)

    model_schema_set.schemas[model_schema.name] = model_schema
    print(model_schema_set.json())
    return model_schema_set


def generate_basic_schema(key: str, data: json, domain: Domain):
    root = __generate_schema(key, data, domain)

    # print(json.dumps(root))

    # print(root.json())
    # TODO[next]  match domain topic

    return root


def link_to_topic_and_factors():
    pass


def save_schema(data: json):
    pass


def __bind_lexicon_to_schema():
    pass


def __bind_entity_to_schema():
    pass
