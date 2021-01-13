
from watchmen.common.log import log
from watchmen.common.utils.copy import direct_copy_raw_schema_to_topic
from watchmen.pipeline.single.pipeline_service import run_pipeline, build_pipeline
from watchmen.space.service.admin import load_space, add_topic_to_space, update_topic_in_space, create_space
from watchmen.space.space import Space
from watchmen.topic.service.topic_service import  create_topic_schema, update_topic_schema
from watchmen.topic.storage.topic_schema_storage import get_raw_topic
from watchmen.topic.topic import Topic


## admin


def test_create_topic():
    log.init()
    topic = {
        "topicId": '1', "code": 'quotation', "name": 'Quota', "type": "distinct",
        "raw": False,

        "factors": [
            {
                "factorId": '101',
                "name": 'quotationId',
                "label": 'Quotation Sequence',
                "type": "sequence"
            },

            {
                "factorId": '103',
                "name": 'quoteDate',
                "label": 'Quotation Create Date',
                "type": "datetime"
            }
        ]
    }

    topic = Topic.parse_obj(topic)
    print(topic.json())
    result = create_topic_schema(topic)

    assert result["_id"] is not None
    # return result


def test_raw_topic():
    print(get_raw_topic("raw_policy"))


# def test_query_topic_list():
#     query_name = "Quota"
#     data_list = query_topic_schema(query_name)
#     print(data_list)


def test_update_topic():
    topic = {
        "topicId": 796064005360713728, "code": 'quotation', "name": 'Quota2222', "type": "distinct",
        "raw": False,

        "factors": [
            {
                "factorId": '101',
                "name": 'quotationId',
                "label": 'Quotation Sequence',
                "type": "sequence"
            },

            {
                "factorId": '103',
                "name": 'quoteDate',
                "label": 'Quotation Create Date',
                "type": "datetime"
            }
        ]
    }

    topic = Topic.parse_obj(topic)
    # data = topic.dict()

    # data["_id"]= ObjectId("5ff415ce2be5eaebbdd08b95")

    topicId = 796064005360713728
    update_topic_schema(topicId, topic)
    # create_topic_schema(data)


def test_create_space():
    space_data = {"spaceId": 1, "name": 'Quotation & Policy', "description": 'All Sales Data'}
    # logging.error("tst start")
    space = Space.parse_obj(space_data)
    # space.name="test_demo"
    create_space(space_data)


def export_http_api_for_raw_data():
    pass


def test_add_topic_to_space():
    space = load_space("test_demo")
    assert space is not None
    model_schema_set = load_raw_schema_by_code("policy")
    policy_topic = model_schema_set.schemas["policy"]
    topic = direct_copy_raw_schema_to_topic(policy_topic, None)
    add_topic_to_space(topic, space)


def test_update_topic_in_space():
    space = load_space("test_demo")
    model_schema_set = load_raw_schema_by_code("policy")
    policy_topic = model_schema_set.schemas["policy"]
    topic = direct_copy_raw_schema_to_topic(policy_topic, None)
    topic.alias = ["test1"]
    return update_topic_in_space(topic, space)


def test_process_raw_data():
    model_schema_set = load_raw_schema_by_code("policy")
    process_raw_data(raw_data_load('../assert/data/policy.json'), model_schema_set, None)


def test_build_pipeline():
    stage_list = [{"name": "split_topic_by_schema",
                   "parameter": {"split_factor": "PolicyStatus", "filter_factor": "policy", "split_factor_value": 2}},
                  {"name": "mapping_to_topic", "parameter": {"mapping_rules": "PolicyId"}},
                  {"name": "insert_topic", "parameter": {"merge_key": "PolicyId", "topic_name": "policy"}}]

    entity_set = import_raw_data(raw_data_load('../assert/data/policy.json'), load_raw_schema_by_code("policy"), None)

    # stage
    # tage("split_topic_by_schema", {"da", "da"})]  stage_list=[S
    pipeline = build_pipeline(stage_list)

    run_pipeline(pipeline, {"data": entity_set})


def test_build_aggregate_pipeline():
    pass


### user


def call_raw_data_collection_api():
    ## call api save raw data
    ## trigger pipeline
    pass


def test_create_subject():
    pass


def test_create_dataset():
    pass


def test_create_report():
    ## create a report query
    pass


def test_run_report():
    pass
    # load_raw_schema(name)

    # find policy schema

    # add topic to space

    # save to space
