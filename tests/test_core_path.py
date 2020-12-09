from watchmen.row_data.storage.row_schema_storage import load_row_schema_by_code
from watchmen.space.service.admin import save_space, load_space, add_topic_to_space, update_topic_in_space
from watchmen.space.space import Space
from watchmen.utils.copy import direct_copy_row_schema_to_topic


def test_create_space():
    space =  Space()
    space.name="test_demo"
    save_space(space)


def test_add_topic_to_space():
    space = load_space("test_demo")
    assert space is not None
    model_schema_set = load_row_schema_by_code("policy")
    policy_topic = model_schema_set.schemas["policy"]
    topic = direct_copy_row_schema_to_topic(policy_topic,None)
    add_topic_to_space(topic,space)


def test_update_topic_in_space():
    space = load_space("test_demo")
    model_schema_set = load_row_schema_by_code("policy")
    policy_topic = model_schema_set.schemas["policy"]
    topic = direct_copy_row_schema_to_topic(policy_topic, None)
    topic.alias=["test1"]
    return update_topic_in_space(topic, space)


def test_build_pipeline():












    pass


def call_row_data_collection_api():
    pass


def test_create_report():
    pass


def test_run_report():
    pass










    #load_row_schema(name)

    #find policy schema

    # add topic to space

    # save to space




