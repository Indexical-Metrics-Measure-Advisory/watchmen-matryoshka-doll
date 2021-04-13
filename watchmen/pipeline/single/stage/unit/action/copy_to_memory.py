import time

from watchmen.common.constants import pipeline_constants
from watchmen.monitor.model.pipeline_monitor import CopyToMemoryAction
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import process_variable, get_source_value_list
from watchmen.topic.topic import Topic


def init(action: UnitAction, pipeline_topic: Topic):
    def copy_to_memory(instance, context):
        raw_data, old_value = instance[pipeline_constants.NEW], instance[pipeline_constants.OLD]
        unit_action_status = CopyToMemoryAction(type=action.type)
        start = time.time()
        variable_type, context_target_name = process_variable(action.variableName)
        value_list = get_source_value_list(pipeline_topic, raw_data, action.source)
        context[context_target_name] = value_list
        elapsed_time = time.time() - start
        unit_action_status.complete_time = elapsed_time
        return context, unit_action_status

    return copy_to_memory
