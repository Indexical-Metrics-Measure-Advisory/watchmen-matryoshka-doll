import datetime
from enum import Enum
from typing import Optional, Dict
from bson import ObjectId
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.raw_data.model_field import ModelField
from watchmen.raw_data.model_relationship import ModelRelationship
from watchmen.raw_data.model_schema import ModelSchema
from watchmen.raw_data.model_schema_set import ModelSchemaSet
from watchmen.raw_data.storage.row_data_schema_storage import load_raw_schema_by_code, insert_data_schema


def convert_value(value):
    if type(value) == ObjectId:
        value = str(value)
    return value


def check_value_type(value):
    if isinstance(value, int):
        return ValueType.INT
    if isinstance(value, str):
        return ValueType.STR
    if isinstance(value, type(True)) or isinstance(value, type(False)):
        return ValueType.BOOLEAN
    if isinstance(value, datetime.datetime):
        return ValueType.DATE
    if isinstance(value, list):
        return ValueType.LIST
    if isinstance(value, dict):
        return ValueType.DICT
    return ValueType.ANY


class ValueType(Enum):
    INT = 1
    STR = 2
    BOOLEAN = 3
    DATE = 4
    LIST = 5
    DICT = 6
    REF = 7
    ANY = 8


def create_raw_data_model_set(code, data):

    def create_schema(name, data, is_root):
        if is_root is None:
            is_root = False

        if type(data) == list:
            for item in data:
                create_model_schema(name, item, is_root)
        else:
            create_model_schema(name, data, is_root)

    def create_model_schema(name, record, is_root):
        model_schema = get_model_schema_by_name(name)
        if model_schema is not None:
            for key, value in record.items():
                if check_model_field_in_schema(key, model_schema):
                    model_schema.businessFields[key].values.append(value)
                else:
                    model_field = create_model_field(key, value);
                    model_schema.businessFields[model_field.name] = model_field
        else:
            model_schema = ModelSchema()
            model_schema.model_id = get_surrogate_key()
            model_schema.name = name
            model_schema.isRoot=is_root
            for key, value in record.items():
                model_field = create_model_field(key, value)
                model_schema.businessFields[model_field.name] = model_field
        schema_set[model_schema.name] = model_schema

    def get_model_schema_by_name(name):
        model_schema_set: ModelSchemaSet = load_raw_schema_by_code(code)
        return model_schema_set.schemas[name]

    def create_model_field(key, value):
        model_filed = ModelField(**{
            'field_id': get_surrogate_key(),
            'name': key,
            'type': check_value_type(value).value,
            'values': [value]
        })
        if model_filed.type == ValueType.LIST.value or model_filed.type == ValueType.DICT.value:
            relationship = ModelRelationship()
            create_schema(key, value)
            relationship.childId=schema_set[key].model_id
            relationships[key]= relationship
        return model_filed

    model_schema_set: ModelSchemaSet= ModelSchemaSet()
    model_schema_set.code = code
    schema_set: Dict[str, ModelSchema] = {}
    relationships: Dict[str, ModelRelationship] = {}
    create_schema(code, data, True)
    model_schema_set.schemas = schema_set
    model_schema_set.relationships = relationships
    insert_data_schema(model_schema_set)


def check_model_field_in_schema(name, model_schema: ModelSchema):
    if model_schema.businessFields[name] is not None:
        return True
    else:
        return False

#class Node(BaseModel):
#    id: int
#    pid: int
#    name: str
#    data_entity: DataEntity = {}
#    child_list: typing.List = []


# class Tree(BaseModel):
#
#     def create_tree(self, pid, name, data):
#         if type(data) == list:
#             return self.create_tree(pid, name, data[0])
#         else:
#             node = Node(**{'id': get_surrogate_key(), 'pid': pid, 'name': name, 'data_entity': {}, 'childs': []})
#             node.pid = pid
#             data_entity = DataEntity()
#             data_entity.entity_id = get_surrogate_key()
#             data_entity.name = name
#             for key, value in data.items():
#                 print(key, value)
#                 attr = Attribute(**{
#                     'name': key,
#                     'type': check_value_type(value).value
#                 })
#                 if attr.type == ValueType.LIST.value or attr.type == ValueType.DICT.value:
#                     node.childs.append(self.create_tree(pid + 1, attr.name, value))
#                 data_entity.attrs.append(attr)
#             node.data_entity = data_entity
#             return node


# Reading the json as a dict, policy information
# with open('policy.json') as json_data:
# with open('test.json') as json_data:
#     policy_data = json.load(json_data, encoding='utf-8')
# schema = generate_schema('policy', policy_data)
# print(schema.json())
# topic_list = crate_topic_by_raw_data_schema(schema, [], [])
# print(topic_list[1].json())
