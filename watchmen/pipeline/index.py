import logging

from watchmen.common.dask.client import get_dask_client
from watchmen.pipeline.single.pipeline_service import run_pipeline
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_by_topic_id
from watchmen.topic.storage.topic_schema_storage import get_topic
log = logging.getLogger("app." + __name__)


def trigger_pipeline(topic_name, instance):
    log.info("trigger_pipeline topic_name :{0}".format(topic_name))
    topic = get_topic(topic_name)
    # TODO validate data with topic schema
    pipeline_list = load_pipeline_by_topic_id(topic.topicId)
    # futures =[]

    for pipeline in pipeline_list:
        log.info("pipeline run: {0}".format(pipeline.json()))
        future = get_dask_client().submit(run_pipeline, pipeline, instance)
        # futures.append(future)

        # print(future.result())
    # for future in futures:
    #     if future.exception()


def trigger_topic(*args, **kwargs):
    topic_name = args[0]
    instance = args[1]
    trigger_pipeline(topic_name, instance)
    # print(instance)
