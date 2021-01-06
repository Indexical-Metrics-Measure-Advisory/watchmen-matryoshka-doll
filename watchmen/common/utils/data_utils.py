from enum import Enum

from watchmen.connector.local_connector import raw_data_load
import os

WATCHMEN = "watchmen"


def build_json_list(files_name,path):
    json_list = []
    for filename in files_name:
        full_path = path+"/"+filename
        if os.path.isfile(full_path):
            json_list.append(raw_data_load(full_path))

    return json_list


def is_field_value(value):
    return type(value) != dict and type(value) != list


def get_dict_schema_set(model_schema_set):
    result = {}
    for schema in model_schema_set.schemas.values():
        result[schema.modelId]= schema
    return result


def get_dict_relationship(model_schema_set):
    result = {}
    for relationship in model_schema_set.relationships.values():
        if relationship.parentId in result.keys():
            result[relationship.parentId].append(relationship)
        else:
            result[relationship.parentId]=[]
            result[relationship.parentId].append(relationship)
    return result


class RelationshipType(Enum):
    OneToOne = "OneToOne"
    OneToMany = "OneToMany"
    ManyToMany = "ManyToMany"