import logging

from watchmen.pipeline.core.index import trigger_pipeline_2
from model.model.pipeline.trigger_type import TriggerType

log = logging.getLogger("app." + __name__)


def trigger_pipeline(topic_name, instance, trigger_type: TriggerType, current_user=None, trace_id=None):
    trigger_pipeline_2(topic_name, instance, trigger_type, current_user, trace_id)
