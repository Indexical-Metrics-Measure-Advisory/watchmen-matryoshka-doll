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


def trigger_pipeline(topic_name, instance, trigger_type: TriggerType, current_user=None):
    trigger_pipeline_2(topic_name, instance, trigger_type, current_user)
