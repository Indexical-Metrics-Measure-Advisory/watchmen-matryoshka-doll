import importlib
import logging
import time
from functools import lru_cache

PIPELINE_CORE_ACTION_ = "watchmen.pipeline.core.action."

log = logging.getLogger("app." + __name__)


@lru_cache(maxsize=16)
def convert_action_type(action_type: str):
    return action_type.replace("-", "_")


def get_action_func(action):
    stage_method = importlib.import_module(PIPELINE_CORE_ACTION_ + convert_action_type(action.type))
    return stage_method


def run_action(action_context):
    action = action_context.action
    stage_method = get_action_func(action)
    func = stage_method.init(action_context)

    start = time.time()
    action_run_status, trigger_pipeline_data_list = func()
    elapsed_time = time.time() - start

    unit = action_context.unitContext.unit
    unit_name = unit.name
    stage = action_context.unitContext.stageContext.stage
    stage_name = stage.name
    pipeline = action_context.unitContext.stageContext.pipelineContext.pipeline
    pipeline_name = pipeline.name

    action_name = action.actionId

    '''
    log.info("run pipeline \"{0}\", stage \"{1}\", unit \"{2}\" action \"{3}\" spend time \"{4}\" ".format(
        pipeline_name, stage_name, unit_name, action_name, elapsed_time))
    '''
    if trigger_pipeline_data_list:
        action_context.unitContext.stageContext.pipelineContext.pipeline_trigger_merge_list = [
            *action_context.unitContext.stageContext.pipelineContext.pipeline_trigger_merge_list,
            *trigger_pipeline_data_list]

    action_context.actionStatus = action_run_status
    return action_context
