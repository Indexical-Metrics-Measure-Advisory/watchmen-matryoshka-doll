# 1. select basic domain for example insurance product ,marketing
# 2. read json from connector
# 3. generate basic raw_data_back base on json data
# 4. match raw_data_back with domain  knowledge dataset and provide suggestions
# 5. link knowledge domain to raw_data_back


from watchmen.connector.local_connector import raw_data_load

from watchmen.pipeline.stage.generate_schema import GenerateLakeSchema
from watchmen.raw_data.service.generate_schema import create_raw_data_model_set
from watchmen.raw_data_back.model_schema import Domain
from watchmen.raw_data_back.service.generate_schema import generate_basic_schema


def test_generate_schema():
    print(generate_basic_schema("policy",raw_data_load('../assert/data/policy.json'),Domain.INSURANCE))


def test_generate_schema_for_list_data():

    GenerateLakeSchema().run([[raw_data_load('../../test/data/policy.json'),raw_data_load('../../test/data/policy.json')],"policy"],{})
    # generate_basic_schema_for_list_data("policy", [raw_data_load('../../test/data/policy.json'),raw_data_load('../../test/data/policy.json')], Domain.INSURANCE)


# def test_generate_schema_for_list_data():

# TODO[next] batch import data and get raw_data_back

# rule = "if the customer’s gender is male, the age is over 60,
# and the main clause limit exceeds 100W,
# then the underwriting level is set to advanced"

def test_raw_data_create_schema():
    create_raw_data_model_set('policy', raw_data_load('../assert/data/policy.json'))

test_raw_data_create_schema()