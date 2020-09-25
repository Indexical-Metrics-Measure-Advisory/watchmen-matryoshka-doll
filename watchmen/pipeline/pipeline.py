import pickle
from watchmen.connector.local_connector import row_data_load
from watchmen.schema.model_schema import Domain
from watchmen.schema.model_schema_set import ModelSchemaSet
from watchmen.service.generate_schema import generate_basic_schema
from watchmen.service.import_data import import_row_data
from watchmen.storage.data_schema_storage import insert_data_schema, update_data_schema


def basic_schema():
    schema = generate_basic_schema("policy", row_data_load('../test/data/policy.json'), Domain.INSURANCE)
    data = schema.dict()
    result = insert_data_schema(data)
    return result.inserted_id


def update_schema():
    id = basic_schema()
    schema = generate_basic_schema("policy", row_data_load('../test/data/policy.json'), Domain.INSURANCE)
    data = schema.dict()
    update_data_schema(id,data)


def import_data():
    pickle_data = pickle.dumps(row_data_load('../test/data/schema.json'))
    model_schema_set = ModelSchemaSet.parse_raw(
        pickle_data, content_type='application/pickle', allow_pickle=True
    )

    # print(type(model_schema_set))
    import_row_data(row_data_load('../test/data/policy.json'),model_schema_set,None)


def run_factors():
    pass


def process_factor_results():
    pass


