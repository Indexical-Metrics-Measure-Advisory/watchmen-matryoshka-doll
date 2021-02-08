import logging

from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.single.pipeline_service import run_pipeline
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_by_topic_id
from watchmen.topic.storage.topic_schema_storage import get_topic

log = logging.getLogger("app." + __name__)


def __match_trigger_type(trigger_type, pipeline):
    return True


def trigger_pipeline(topic_name, instance, trigger_type: TriggerType):
    log.info("trigger_pipeline topic_name :{0}".format(topic_name))
    topic = get_topic(topic_name)
    # TODO validate data with topic schema
    pipeline_list = load_pipeline_by_topic_id(topic.topicId)
    # futures =[]

    for pipeline in pipeline_list:
        if __match_trigger_type(trigger_type, pipeline):
            log.debug("pipeline run: {0}".format(pipeline.json()))
            run_pipeline(pipeline, instance)
