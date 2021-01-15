from watchmen.pipeline.single.pipeline_service import run_pipeline
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_by_topic_id
from watchmen.topic.storage.topic_schema_storage import get_raw_topic


def test_save_topic_instance():
    data = {
        "permium": 12020,
        "policyNo": "N001",
        "policyId": 1234,
        "customers": [
            {"name": "CK","age":1},
            {"name": "ADD", "age": 2}
        ]
    }

    topic = get_raw_topic("raw_policy")
    # TODO validate data with topic schema
    # print("topic.topicId:", topic.topicId)
    pipeline_list = load_pipeline_by_topic_id(topic.topicId)

    for pipeline in pipeline_list:
        run_pipeline(pipeline, data)
    # save_topic_instance("raw_policy", data)
