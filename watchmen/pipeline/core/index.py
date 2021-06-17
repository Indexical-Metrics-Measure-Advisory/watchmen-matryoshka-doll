import logging

from distributed import fire_and_forget, as_completed

from watchmen.common.dask.client import get_dask_client
from watchmen.pipeline.core.context.pipeline_context import PipelineContext
from watchmen.pipeline.core.worker.pipeline_worker import run_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_by_topic_id
from watchmen.topic.storage.topic_schema_storage import get_topic

log = logging.getLogger("app." + __name__)


def __match_trigger_type(trigger_type, pipeline):
    if trigger_type == TriggerType.insert and (pipeline.type == "insert-or-merge" or pipeline.type == "insert"):
        return True
    elif trigger_type == TriggerType.update and (pipeline.type == "insert-or-merge" or pipeline.type == "update"):
        return True
    elif trigger_type == TriggerType.delete and pipeline.type == "delete":
        return True
    else:
        return False


def trigger_pipeline_2(topic_name, instance, trigger_type: TriggerType):
    # log.info("trigger_pipeline topic_name :{0}".format(topic_name))
    topic = get_topic(topic_name)
    pipeline_list = load_pipeline_by_topic_id(topic.topicId)
    # client = get_dask_client()

    # import_raw_topic_data(topic_event)
    run_pipeline_list =[]
    pipeline_contexts = []
    for pipeline in pipeline_list:
        if __match_trigger_type(trigger_type, pipeline):
            # run_pipeline_list.append(pipeline)
            # log.info("pipeline run: {0}".format(pipeline.json()))
            pipeline_context = PipelineContext(pipeline, instance)
            # pipeline_contexts.append(pipeline_context)
            # task = client.submit(run_pipeline, pipeline_context)
            # fire_and_forget(task)
            # task.
            run_pipeline(pipeline_context)
    # futures = client.map(run_pipeline, pipeline_contexts)
    #
    # seq = as_completed(futures)
    #
    # for future in seq:
    #       future.result()





