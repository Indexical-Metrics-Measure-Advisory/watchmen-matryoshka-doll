from watchmen.schema.model_schema_set import ModelSchemaSet


def is_field_value(value):
    return type(value) != dict and type(value) != list


def get_dict_schema_set(model_schema_set:ModelSchemaSet):
    result = {}
    for schema in model_schema_set.schemas:
        result[schema.modelId]=schema
    return result


def get_dict_relationship(model_schema_set:ModelSchemaSet):
    result = {}
    for relationship in model_schema_set.relationships:
        result[relationship.parentId]=relationship
    return result
