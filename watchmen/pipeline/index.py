import dask

from watchmen.pipeline.storage.pipeline_storage import load_pipeline_by_topic_id
from watchmen.topic.storage.topic_schema_storage import get_raw_topic


def trigger_pipeline(topic_name,instance):
    topic = get_raw_topic(topic_name)
    # TODO validate data with topic schema
    pipeline_list = load_pipeline_by_topic_id(topic.topicId)
    # flow = None
    for pipeline in pipeline_list:
        print("run:",pipeline)
    #     flow = dask.delayed(pipeline)(pipeline_event.data)
    #
    # flow.compute()

    # TODO  future run

    # load relationship pipeline by topic id
    # multiple process run pipeline
    # sent backend task for monitor topic data


def trigger_topic(*args,**kwargs):
    topic_name = args[0]
    instance = args[1]

    trigger_pipeline(topic_name,instance)
    # print(instance)




