from dask.distributed import Client

from watchmen.pipeline.single.pipeline_service import run_pipeline
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_by_topic_id
from watchmen.topic.storage.topic_schema_storage import get_raw_topic

client = Client()


def trigger_pipeline(topic_name, instance):
    topic = get_raw_topic(topic_name)
    # TODO validate data with topic schema
    # print("topic.topicId:", topic.topicId)
    pipeline_list = load_pipeline_by_topic_id(topic.topicId)
    # flow = None

    for pipeline in pipeline_list:
        # TODO  use dask task submit for pipeline
        # print("run:",pipeline.json())
        future = client.submit(run_pipeline, pipeline, instance)

        print(future.result())


def trigger_topic(*args, **kwargs):
    topic_name = args[0]
    instance = args[1]

    trigger_pipeline(topic_name, instance)
    # print(instance)
