import json

from bson import ObjectId

from watchmen.connector.local_connector import row_data_load
from watchmen.space.factors.factor import Factor
from watchmen.index import select_domain, generate_lake_schema, save_topic_mapping
from watchmen.row_data import ModelField
from watchmen.pipeline.mapping import MappingRule
from watchmen.pipeline.mapping import generate_topic_suggestion, generate_factor_suggestion
from watchmen.pipeline.mapping import TopicMappingRule
from watchmen.row_data.storage.row_schema_storage import load_row_schema_by_code
from watchmen.storage.mapping_rule_storage import load_topic_mapping_by_name, load_topic_mapping_by_id
from watchmen.space.storage.space_storage import  load_space_by_name
from watchmen.storage.topic_schema_storage import get_topic_list_by_ids


def test_select_domain():
    master_space  = select_domain("insurance")
    assert master_space is not None


def test_import_instance_data():
    generate_lake_schema([row_data_load('../assert/data/policy.json'),row_data_load('../assert/data/policy.json')],"policy")


def test_save_topic_mapping_rule():
    topic_mapping_rule = TopicMappingRule()
    topic_mapping_rule.targetTopicId="123"
    topic_mapping_rule.sourceTopicId="235"
    topic_mapping_rule.targetTopicName="test1"
    topic_mapping_rule.sourceTopicName="test"
    factor_mapping_rule = MappingRule()
    factor_mapping_rule.isBucket=True
    factor_mapping_rule.masterFactor = Factor()
    factor_mapping_rule.lateField = ModelField()
    topic_mapping_rule.factor_rules["DD"]=factor_mapping_rule
    save_topic_mapping(topic_mapping_rule)


def test_generate_factor_suggestion():
    lake_schema = load_row_schema_by_code("policy")
    master_schema = load_space_by_name("mock_insurance")
    topic_id_list = master_schema.topic_id_list
    object_ids = map(lambda x: ObjectId(x), topic_id_list)
    topic_list = get_topic_list_by_ids(list(object_ids))

    model_schema =lake_schema.schemas["policy"]

    # for topic in topic_list:
    #     print(topic)

    matches = (topic for topic in topic_list if topic['topic_name'] =="policy")
    # master_schema.topic_id_list

    for match_topic in list(matches):
        results =generate_factor_suggestion(model_schema,match_topic)
        # print(results)
        print(json.dumps(results))
    # lake_schema.


def test_load_topic_mapping_rule():
    print(load_topic_mapping_by_id("123","235"))


def test_load_topic_mapping_rule():
    print(load_topic_mapping_by_name("test","test1"))


def test_generate_suggestion():
    lake_schema = load_row_schema_by_code("policy")
    master_schema = load_space_by_name("mock_insurance")
    topic_id_list = master_schema.topic_id_list
    object_ids = map(lambda x: ObjectId(x), topic_id_list)
    topic_list = get_topic_list_by_ids(list(object_ids))
    print(json.dumps(generate_topic_suggestion(lake_schema,topic_list)))


# def test_generate_suggestion_factor():
#     lake_schema = load_data_schema_by_code("policy")
#     master_schema = load_master_space_by_name("mock_insurance")
#     topic_id_list = master_schema.topic_id_list
#     object_ids = map(lambda x: ObjectId(x), topic_id_list)
#     topic_list = get_topic_list_by_ids(list(object_ids))
#     print(json.dumps(generate_topic_suggestion(lake_schema,topic_list)))
