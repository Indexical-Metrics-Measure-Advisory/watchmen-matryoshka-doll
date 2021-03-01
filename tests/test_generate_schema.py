# 1. select basic domain for example insurance product ,marketing
# 2. read json from connector
# 3. generate basic raw_data_back base on json data
# 4. match raw_data_back with domain  knowledge dataset and provide suggestions
# 5. link knowledge domain to raw_data_back


import os

# from watchmen.collection.connector import raw_data_load
from watchmen.collection.connector.local_connector import raw_data_load
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.raw_data.service.generate_schema import create_raw_data_model_set
# def test_generate_schema():
#     print(generate_basic_schema("policy", raw_data_load('../assert/data/policy.json'), Domain.INSURANCE))
from watchmen.topic.factor.factor import Factor
from watchmen.topic.service.topic_service import create_topic_schema
from watchmen.topic.topic import Topic


def __build_json_list(files_name, path):
    json_list = []
    for filename in files_name:
        full_path = path + "/" + filename
        if os.path.isfile(full_path):
            json_list.append(raw_data_load(full_path))

    return json_list


def __have_parent(parent_name, whole_relation,root_name):
    for key,relationship in whole_relation.items():
        if key == parent_name and relationship.parentName == root_name:
            return parent_name
        else:
            if key == parent_name:
                return __have_parent(relationship.parentName,whole_relation,root_name)+"."+parent_name



def test_have_parent():
    path = '/Users/yifeng/PycharmProjects/ebaogi-data-collection/collection_data/PGA'
    files_name = os.listdir(path)
    json_list = __build_json_list(files_name, path)
    # print(json_list)
    result = create_raw_data_model_set('raw_gi_policy', json_list)
    # print(result.json())


    print(__have_parent("PolicyCoverageList",result.relationships,"raw_gi_policy"))




# def get_parent_name(whole_relation,schema_name ,parent_name):
#     if have_parent(parent_name,whole_relation)



def __build_sub_factors(relationship_keys, result_relationships, factor_list, schemas, root_name,whole_relation):
    result = {}
    key_list = []
    #

    for key, relationship in result_relationships.items():
        if relationship.parentName in relationship_keys:
            schema = schemas[key]
            nest_factor = Factor()
            nest_factor.name = __have_parent(schema.name,whole_relation,root_name)
            nest_factor.label = schema.name
            nest_factor.type = "array"
            nest_factor.factorId = get_surrogate_key()
            key_list.append(key)
            # if factor_parent_name is not None:
            #     factor_parent_name = factor_parent_name + "." + schema.name
            factor_list.append(nest_factor)
            for field_key, field in schema.businessFields.items():
                factor = Factor()
                factor.factorId = get_surrogate_key()
                factor.name = __have_parent(schema.name,whole_relation,root_name)+"."+field.name
                factor.label = factor.name
                factor.type = field.type
                factor_list.append(factor)
        else:
            result[key] = relationship
            # result[key] = None
            # print(relationships)
    return result, key_list


def test_generate_schema_for_list_data():
    path = '/Users/yifeng/PycharmProjects/ebaogi-data-collection/collection_data/pinkcloud-claim'
    files_name = os.listdir(path)
    json_list = __build_json_list(files_name, path)
    # print(json_list)
    result = create_raw_data_model_set('raw_pinkcloud_claim', json_list)
    # print(result.json())

    root_name = result.code

    root_node = result.schemas[root_name]
    # print(root_node)

    topic = Topic()
    topic.topicId = get_surrogate_key()
    topic.name = root_name
    topic.code = root_name
    topic.type = "raw"
    topic.factors = []
    for key, field in root_node.businessFields.items():
        factor = Factor()
        factor.name = key
        factor.type = field.type
        factor.factorId = get_surrogate_key()
        factor.label = key
        topic.factors.append(factor)

    relationships = result.relationships

    result_relationships, key_list = __build_sub_factors([root_node.name], relationships, topic.factors, result.schemas,
                                                         root_name,relationships)

    # print (type(result_relationships))
    flag = bool(result_relationships)

    while flag:
        # print("before key_list：",key_list)
        # print("relationships:", result_relationships)

        result_relationships, key_list = __build_sub_factors(key_list, result_relationships, topic.factors,
                                                                   result.schemas,
                                                                    root_name,relationships)
        # print("after key_list：", key_list)
        # print("relationships:", result_relationships)

        flag = bool(result_relationships)





    # result_relationships, key_list = __build_sub_factors(key_list, result_relationships, topic.factors,
    #                                                      result.schemas,
    #                                                      key)


    # print(key_list)

            # print("result_relationships", result_relationships)
            # print("result_relationships", bool(result_relationships))
            # flag = bool(result_relationships)


# print(relationships)
    print(topic.json())
    create_topic_schema(topic)


# del relationships[relationship.name]
# # create_topic_schema(topic)
# for key ,relationship in root_node.relationships.items():
#     pass

# GenerateLakeSchema().run([[raw_data_load('../../test/data/policy.json'),raw_data_load('../../test/data/policy.json')],"policy"],{})
# generate_basic_schema_for_list_data("policy", [raw_data_load('../../test/data/policy.json'),raw_data_load('../../test/data/policy.json')], Domain.INSURANCE)


# def test_generate_schema_for_list_data():


# rule = "if the customer’s gender is male, the age is over 60,
# and the main clause limit exceeds 100W,
# then the underwriting level is set to advanced"

def test_raw_data_create_schema():
    result = create_raw_data_model_set('policy', raw_data_load('../assert/data/policy.json'))

    print(result.json())

# test_raw_data_create_schema()
