from enum import Enum

WATCHMEN = "watchmen"


def is_field_value(value):
    return type(value) != dict and type(value) != list


def get_dict_schema_set(model_schema_set):
    result = {}
    for schema in model_schema_set.schemas:
        result[schema.modelId]=schema
    return result


def get_dict_relationship(model_schema_set):
    result = {}
    for relationship in model_schema_set.relationships:
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