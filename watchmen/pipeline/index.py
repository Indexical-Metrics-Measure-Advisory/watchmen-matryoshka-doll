import logging

from watchmen.pipeline.core.index import trigger_pipeline_2
from watchmen.pipeline.model.trigger_type import TriggerType

log = logging.getLogger("app." + __name__)


def trigger_pipeline(topic_name, instance, trigger_type: TriggerType, current_user=None):
    trigger_pipeline_2(topic_name, instance, trigger_type, current_user)
