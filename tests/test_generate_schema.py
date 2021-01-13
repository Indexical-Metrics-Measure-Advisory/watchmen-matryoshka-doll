# 1. select basic domain for example insurance product ,marketing
# 2. read json from connector
# 3. generate basic raw_data_back base on json data
# 4. match raw_data_back with domain  knowledge dataset and provide suggestions
# 5. link knowledge domain to raw_data_back


import os

from watchmen.raw_data_back.model_schema import Domain
from watchmen.raw_data_back.service.generate_schema import generate_basic_schema

from watchmen.collection.connector import raw_data_load
from watchmen.raw_data.service.generate_schema import create_raw_data_model_set


def test_generate_schema():
    print(generate_basic_schema("policy", raw_data_load('../assert/data/policy.json'), Domain.INSURANCE))


def __build_json_list(files_name, path):
    json_list = []
    for filename in files_name:
        full_path = path + "/" + filename
        if os.path.isfile(full_path):
            json_list.append(raw_data_load(full_path))

    return json_list


def test_generate_schema_for_list_data():
    path = '/Users/yifeng/PycharmProjects/ebaogi-data-collection/collection_data/PGA'
    files_name = os.listdir(path)
    json_list = __build_json_list(files_name, path)
    print(json_list)
    result = create_raw_data_model_set('policy—2', json_list)
    print(result.json())

    # GenerateLakeSchema().run([[raw_data_load('../../test/data/policy.json'),raw_data_load('../../test/data/policy.json')],"policy"],{})
    # generate_basic_schema_for_list_data("policy", [raw_data_load('../../test/data/policy.json'),raw_data_load('../../test/data/policy.json')], Domain.INSURANCE)


# def test_generate_schema_for_list_data():

# TODO[next] batch import data and get raw_data_back

# rule = "if the customer’s gender is male, the age is over 60,
# and the main clause limit exceeds 100W,
# then the underwriting level is set to advanced"

def test_raw_data_create_schema():
    result = create_raw_data_model_set('policy', raw_data_load('../assert/data/policy.json'))

    print(result.json())

# test_raw_data_create_schema()
