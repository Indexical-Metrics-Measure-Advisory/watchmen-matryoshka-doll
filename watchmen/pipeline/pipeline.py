import pickle
from watchmen.connector.local_connector import row_data_load
from watchmen.schema.model_schema import Domain
from watchmen.schema.model_schema_set import ModelSchemaSet
from watchmen.service.generate_schema import generate_basic_schema
from watchmen.service.import_data import import_row_data
from watchmen.storage.data_schema_storage import insert_data_schema, update_data_schema


def basic_schema(json,domain=None):
    schema = generate_basic_schema("policy", json, domain)
    data = schema.dict()
    result = insert_data_schema(data)
    return result.inserted_id


def update_schema(id, json,domain=None):
    schema = generate_basic_schema("policy",json,domain)
    data = schema.dict()
    return update_data_schema(id,data)


def import_data(json,schema):

    # print(type(model_schema_set))
    return import_row_data(json,schema,None)


def run_factors():
    pass


def process_factor_results():
    pass


