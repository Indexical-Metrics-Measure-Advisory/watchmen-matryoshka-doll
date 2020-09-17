
# TODO (next)
import pprint
from watchmen.connector.local_connector import row_data_load
from watchmen.schema.model_schema import Domain
from watchmen.service.generate_schema import generate_basic_schema
from watchmen.storage.data_schema_storage import insert_data_schema, load_data_schema_by_name


def basic_schema():
    schema = generate_basic_schema("policy", row_data_load('../test/data/policy.json'), Domain.INSURANCE)
    data = schema.dict()
    result = insert_data_schema(data)

    pprint.pprint(load_data_schema_by_name(result.inserted_id))
