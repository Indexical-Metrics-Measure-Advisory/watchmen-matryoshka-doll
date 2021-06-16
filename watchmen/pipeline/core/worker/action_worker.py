import logging

from watchmen.pipeline.core.context.action_context import get_variables
from watchmen.pipeline.single.pipeline_service import find_action_type_func, convert_action_type

log = logging.getLogger("app." + __name__)


def run_action(actionContext):
    action = actionContext.action
    pipeline_topic = actionContext.unitContext.stageContext.pipelineContext.pipelineTopic
    func = find_action_type_func(convert_action_type(action.type), action,
                                 pipeline_topic)
    # call dynamic action in action folder
    # TODO [future] custom folder
    out_result, unit_action_status, trigger_pipeline_data_list = func(
        actionContext.unitContext.stageContext.pipelineContext.data,
        get_variables(actionContext))

    if trigger_pipeline_data_list:
        actionContext.unitContext.stageContext.pipelineContext.pipeline_trigger_merge_list = [
            *actionContext.unitContext.stageContext.pipelineContext.pipeline_trigger_merge_list,
            *trigger_pipeline_data_list]

    # log.info("out_result :{0}".format(out_result))
    actionContext.unitContext.stageContext.pipelineContext.variables = {
        **actionContext.unitContext.stageContext.pipelineContext.variables,
        **out_result}
    actionContext.actionStatus = unit_action_status
