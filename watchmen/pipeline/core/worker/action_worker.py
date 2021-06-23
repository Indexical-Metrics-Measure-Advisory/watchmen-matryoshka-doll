import importlib
import logging
import time

from watchmen.pipeline.core.context.action_context import get_variables
from watchmen.pipeline.single.pipeline_service import find_action_type_func, convert_action_type

log = logging.getLogger("app." + __name__)


def run_action(actionContext):
    action = actionContext.action

    stage_method = importlib.import_module("watchmen.pipeline.core.action." + convert_action_type(action.type))
    func = stage_method.init(actionContext)

    start = time.time()
    action_run_status, trigger_pipeline_data_list = func()
    elapsed_time = time.time() - start

    unit = actionContext.unitContext.unit
    unit_name = unit.name
    stage = actionContext.unitContext.stageContext.stage
    stage_name = stage.name
    pipeline = actionContext.unitContext.stageContext.pipelineContext.pipeline
    pipeline_name = pipeline.name

    action_name = action.actionId

    log.info("run pipeline \"{0}\", stage \"{1}\", unit \"{2}\" action \"{3}\" spend time \"{4}\" ".format(
        pipeline_name, stage_name, unit_name, action_name, elapsed_time))

    if trigger_pipeline_data_list:
        actionContext.unitContext.stageContext.pipelineContext.pipeline_trigger_merge_list = [
            *actionContext.unitContext.stageContext.pipelineContext.pipeline_trigger_merge_list,
            *trigger_pipeline_data_list]

    actionContext.actionStatus = action_run_status
