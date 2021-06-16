import logging

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

    for pipeline in pipeline_list:
        if __match_trigger_type(trigger_type, pipeline):
            # log.info("pipeline run: {0}".format(pipeline.json()))
            pipelineContext = PipelineContext(pipeline, instance)
            run_pipeline(pipelineContext)
