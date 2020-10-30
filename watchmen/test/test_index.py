from watchmen.connector.local_connector import row_data_load
from watchmen.factors.model.factor import Factor
from watchmen.index import select_domain, generate_lake_schema, save_topic_mapping, load_topic_mapping
from watchmen.lake.model_field import ModelField
from watchmen.mapping.mapping_rule import MappingRule
from watchmen.mapping.suggestion.generate_suggestion import generate_topic_suggestion
from watchmen.mapping.topic_mapping_rule import TopicMappingRule
from watchmen.storage.data_schema_storage import load_data_schema_by_code
from watchmen.storage.master_storage import load_master_space_by_user


def test_select_domain():
    master_space  = select_domain("insurance")

    assert master_space is not None


def test_import_instance_data():
    # data =
    # # data2 = row_data_load('../../test/data/policy.json')
    generate_lake_schema([row_data_load('../../test/data/policy.json'),row_data_load('../../test/data/policy.json')],"policy")


def test_save_topic_mapping_rule():
    topic_mapping_rule = TopicMappingRule()
    topic_mapping_rule.lakeSchemaId="123"
    topic_mapping_rule.targetTopicId="235"
    factor_mapping_rule = MappingRule()
    factor_mapping_rule.isBucket=True
    factor_mapping_rule.masterFactor = Factor()
    factor_mapping_rule.lateField = ModelField()
    topic_mapping_rule.factor_rules["DD"]=factor_mapping_rule
    save_topic_mapping(topic_mapping_rule)


def test_load_topic_mapping_rule():
    print(load_topic_mapping("123","235"))


def test_generate_suggestion():
    lake_schema = load_data_schema_by_code("policy")
    master_schema = load_master_space_by_user("mock")
    print( generate_topic_suggestion(lake_schema,master_schema))




    # load lake_schema
    # load master_schema
    # generate_suggestion()





    pass