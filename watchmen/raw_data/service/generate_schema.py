import datetime
import json
import typing
from enum import Enum

from bson import ObjectId
from pydantic import BaseModel

from watchmen.common.snowflake.snowflake import get_surrogate_key

from watchmen.raw_data.data_entity import DataEntity, Attribute
from watchmen.raw_data.service.import_raw_data import crate_topic_by_raw_data_schema


NODE = "NODE_"
ATTR = "ATTR_"


def generate_schema(schema_name, data: json):
    # tree = Tree()
    return create_tree(0, schema_name, data,{})


def generate_schema_for_list_data(schema_name: str, data_list: []):

    context = {}
    node ={}
    for data in data_list:
         node= create_tree(0, schema_name, data, context)

    return node



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


class Node(BaseModel):
    id: int
    pid: int
    name: str
    data_entity: DataEntity = {}
    child_list: typing.List = []


def get_exist_or_create_node(pid,name,context:dict):
    key = build_data_node_key(name)
    if key in context.keys():
        return context[key]
    else:
        node = Node(**{'id': get_surrogate_key(), 'pid': pid, 'name': name, 'data_entity': {}, 'childs': []})
        data_entity = DataEntity()
        data_entity.entity_id = get_surrogate_key()
        data_entity.name = name
        node.data_entity = data_entity
        context[key] = node
        return node


def get_exist_or_create_attr(name, value, context):
    key = build_data_attr_key(name)
    if key in context.keys():
        attr = context[key]
        if value not in attr.values():
            attr.values().append(convert_value(value))
    else:
        attr = Attribute(**{
            'name': name,
            'type': check_value_type(value).value

        })

        attr.values.append(convert_value(value))
        return attr


def build_data_attr_key(name):
    return ATTR + name


def build_data_node_key(name):
    return NODE+name


def create_tree( pid, name, data,context: dict):
    if type(data) == list:
        return create_tree(pid, name, data[0],context)
    else:
        node = get_exist_or_create_node(pid,name,context)
        for key, value in data.items():
            attr = get_exist_or_create_attr(key,value,context)

            if attr.type == ValueType.LIST.value or attr.type == ValueType.DICT.value:
                node.child_list.append(create_tree(pid + 1, attr.name, value, context))
            node.data_entity.attrs.append(attr)
        return node


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
