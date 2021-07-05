import logging

from watchmen.pipeline.core.index import trigger_pipeline_2
from watchmen.pipeline.model.trigger_type import TriggerType

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


'''
def trigger_pipeline(topic_name, instance, trigger_type: TriggerType):
    log.info("trigger_pipeline topic_name :{0}".format(topic_name))
    topic = get_topic(topic_name)
    pipeline_list = load_pipeline_by_topic_id(topic.topicId)

    for pipeline in pipeline_list:
        if __match_trigger_type(trigger_type, pipeline):
            # log.info("pipeline run: {0}".format(pipeline.json()))
            run_pipeline(pipeline, instance)
'''


def trigger_pipeline(topic_name, instance, trigger_type: TriggerType,current_user=None):
    trigger_pipeline_2(topic_name, instance, trigger_type,current_user)
