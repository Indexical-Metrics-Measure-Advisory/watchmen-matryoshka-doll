import json
import datetime
import typing
from enum import Enum
import os

from pydantic import BaseModel

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.raw_data.data_entity import DataEntity, Attribute
from watchmen.raw_data import crate_topic_by_raw_data_schema


def generate_schema(schema_name, data: json):
    tree = Tree()
    return tree.create_tree(0, schema_name, data)


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
    data_entity: DataEntity
    childs: typing.List


class Tree(BaseModel):
    def create_tree(self, pid, name, data):
        if type(data) == list:
            return self.create_tree(pid, name, data[0])
        else:
            node = Node(**{'id': get_surrogate_key(), 'pid': pid, 'name': name, 'data_entity': {}, 'childs': []})
            node.pid = pid
            data_entity = DataEntity()
            data_entity.entity_id = get_surrogate_key()
            data_entity.name = name
            for key, value in data.items():
                print(key, value)
                attr = Attribute(**{
                    'name': key,
                    'type': check_value_type(value).value
                })
                if attr.type == ValueType.LIST.value or attr.type == ValueType.DICT.value:
                    node.childs.append(self.create_tree(pid + 1, attr.name, value))
                data_entity.attrs.append(attr)
            node.data_entity = data_entity
            return node


# Reading the json as a dict, policy information
# with open('policy.json') as json_data:
with open('test.json') as json_data:
    policy_data = json.load(json_data, encoding='utf-8')
schema = generate_schema('policy', policy_data)
print(schema.json())
topic_list = crate_topic_by_raw_data_schema(schema, [], [])
print(topic_list[1].json())
