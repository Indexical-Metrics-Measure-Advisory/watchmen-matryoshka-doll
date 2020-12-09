import pickle

from watchmen.connector.local_connector import raw_data_load
from watchmen.pipeline.single.pipeline_service import run_pipeline, build_pipeline
from watchmen.raw_data.model_schema_set import ModelSchemaSet
from watchmen.raw_data.service.import_data import process_raw_data
from watchmen.raw_data.storage.row_schema_storage import load_raw_schema_by_code
from watchmen.space.service.admin import save_space, load_space, add_topic_to_space, update_topic_in_space
from watchmen.space.space import Space
from watchmen.utils.copy import direct_copy_raw_schema_to_topic


def test_create_space():
    space = Space()
    space.name="test_demo"
    save_space(space)


def test_add_topic_to_space():
    space = load_space("test_demo")
    assert space is not None
    model_schema_set = load_raw_schema_by_code("policy")
    policy_topic = model_schema_set.schemas["policy"]
    topic = direct_copy_raw_schema_to_topic(policy_topic,None)
    add_topic_to_space(topic,space)


def test_update_topic_in_space():
    space = load_space("test_demo")
    model_schema_set = load_raw_schema_by_code("policy")
    policy_topic = model_schema_set.schemas["policy"]
    topic = direct_copy_raw_schema_to_topic(policy_topic, None)
    topic.alias=["test1"]
    return update_topic_in_space(topic, space)


def test_process_raw_data():

    model_schema_set = load_raw_schema_by_code("policy")

    print(model_schema_set.json())
    process_raw_data(raw_data_load('../assert/data/policy.json'),model_schema_set,None)



def test_build_pipeline():
    stage_list = [{"name": "split_topic_by_schema", "parameter": {"split_factor": "PolicyStatus"}},
                  {"name": "merge_to_topic", "parameter": {"key": "PolicyId"}}]







    # stage
    # tage("split_topic_by_schema", {"da", "da"})]  stage_list=[S
    pipeline = build_pipeline(stage_list)

    run_pipeline(pipeline, {"topic_a": "dadas"})

    pass


def call_raw_data_collection_api():
    pass


def test_create_report():
    pass


def test_run_report():
    pass










    #load_raw_schema(name)

    #find policy schema

    # add topic to space

    # save to space




