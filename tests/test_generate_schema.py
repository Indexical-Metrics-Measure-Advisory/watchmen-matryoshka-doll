# 1. select basic domain for example insurance product ,marketing
# 2. read json from connector
# 3. generate basic lake base on json data
# 4. match lake with domain  knowledge dataset and provide suggestions
# 5. link knowledge domain to lake


from watchmen.connector.local_connector import row_data_load
from watchmen.lake.model_schema import Domain
from watchmen.pipeline.stage.generate_schema import GenerateLakeSchema
from watchmen.service.generate_schema import generate_basic_schema, generate_basic_schema_for_list_data


def test_generate_schema():
    generate_basic_schema("policy",row_data_load('../../test/data/policy.json'),Domain.INSURANCE)


def test_generate_schema_for_list_data():

    GenerateLakeSchema().run([[row_data_load('../../test/data/policy.json'),row_data_load('../../test/data/policy.json')],"policy"],{})
    # generate_basic_schema_for_list_data("policy", [row_data_load('../../test/data/policy.json'),row_data_load('../../test/data/policy.json')], Domain.INSURANCE)


# def test_generate_schema_for_list_data():

# TODO[next] batch import data and get lake

# rule = "if the customer’s gender is male, the age is over 60,
# and the main clause limit exceeds 100W,
# then the underwriting level is set to advanced"

