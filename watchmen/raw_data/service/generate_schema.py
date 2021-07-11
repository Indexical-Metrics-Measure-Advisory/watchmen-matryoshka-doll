import datetime
from enum import Enum
from typing import Any

from bson import ObjectId
from pydantic import BaseModel

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.raw_data.model_field import ModelField
from watchmen.raw_data.model_relationship import ModelRelationship
from watchmen.raw_data.model_schema import ModelSchema
from watchmen.raw_data.model_schema_set import ModelSchemaSet


class RawTopicGenerateEvent(BaseModel):
    code: str = None
    data: Any = None


def convert_value(value):
    if type(value) == ObjectId:
        value = str(value)
    return value


def check_value_type(value):
    if isinstance(value, int):
        return ValueType.INT.value
    if isinstance(value, float):
        return ValueType.INT.value
    if isinstance(value, str):
        return ValueType.STR.value
    if isinstance(value, type(True)) or isinstance(value, type(False)):
        return ValueType.BOOLEAN.value
    if isinstance(value, datetime.datetime):
        return ValueType.DATE.value
    if isinstance(value, list):
        return ValueType.LIST.value
    if isinstance(value, dict):
        return ValueType.DICT.value
    return ValueType.ANY.value


class ValueType(Enum):
    INT = "number"
    STR = "text"
    BOOLEAN = "boolean"
    DATE = "datetime"
    LIST = "array"
    DICT = "dict"
    REF = "ref"
    ANY = "any"


'''
def create_raw_data_model_set(code, data):
    model_schema_set = get_model_schema_set_by_code(code)
    if model_schema_set is not None:
        create_schema(model_schema_set, code, data, True)
        update_data_schema(model_schema_set.id, model_schema_set.dict())
    else:
        model_schema_set = ModelSchemaSet()
        model_schema_set.id = get_surrogate_key()
        model_schema_set.code = code
        model_schema_set.schemas = {}
        model_schema_set.relationships = {}
        create_schema(model_schema_set, code, data, True)
        insert_data_schema(model_schema_set.dict())

    return model_schema_set
'''


def create_raw_data_model_set(code, data):
    model_schema_set = ModelSchemaSet()
    model_schema_set.id = get_surrogate_key()
    model_schema_set.code = code
    model_schema_set.schemas = {}
    model_schema_set.relationships = {}
    create_schema(model_schema_set, code, data, True)
    # insert_data_schema(model_schema_set.dict())
    return model_schema_set


def create_schema(model_schema_set, name, data, is_root):
    if is_root is None:
        is_root = False

    if type(data) == list and len(data) > 0:
        for item in data:
            create_model_schema(model_schema_set, name, item, is_root)
    elif type(data) == list and len(data) == 0:
        pass
    else:
        create_model_schema(model_schema_set, name, data, is_root)


def create_model_schema(model_schema_set, name, record, is_root):
    model_schema = model_schema_set.schemas.get(name)
    if model_schema is not None:
        for key, value in record.items():
            if check_model_field_in_schema(key, model_schema):
                if check_value_type(value) == ValueType.LIST.value or check_value_type(
                        value) == ValueType.DICT.value:
                    create_schema(model_schema_set, key, value, False)
            else:
                model_field = create_model_field(model_schema_set, model_schema, key, value)
                model_schema.businessFields[model_field.name] = model_field
    else:
        model_schema = ModelSchema()
        model_schema.model_id = get_surrogate_key()
        model_schema.name = name
        model_schema.isRoot = is_root

        for key, value in record.items():
            model_field = create_model_field(model_schema_set, model_schema, key, value)
            model_schema.businessFields[model_field.name] = model_field
    model_schema_set.schemas[model_schema.name] = model_schema


def create_model_field(model_schema_set, model_schema, key, value):
    model_filed = ModelField(**{
        'field_id': get_surrogate_key(),
        'name': key,
        'type': check_value_type(value)
    })
    if type(value) == list and len(value) == 0:
        return model_filed
    elif model_filed.type == ValueType.LIST.value or model_filed.type == ValueType.DICT.value:
        relationship = ModelRelationship()
        create_schema(model_schema_set, key, value, False)
        relationship.parentId = model_schema.model_id
        relationship.parentName = model_schema.name
        relationship.childId = model_schema_set.schemas[key].model_id
        relationship.childName = model_schema_set.schemas[key].name
        model_schema_set.relationships[key] = relationship

    return model_filed


def check_model_field_in_schema(name, model_schema: ModelSchema):
    if name in model_schema.businessFields:
        return True
    else:
        return False


# def get_model_schema_set_by_code(code):
#     model_schema_set_dict = load_raw_schema_by_code(code)
#     if model_schema_set_dict is not None:
#         model_schema_set = ModelSchemaSet(**model_schema_set_dict)
#         return model_schema_set
#     else:
#         return None


def check_value_duplicate(values, value):
    return value in values
