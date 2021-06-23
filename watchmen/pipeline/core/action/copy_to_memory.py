import time

from watchmen.pipeline.core.context.action_context import ActionContext, set_variable, get_variables
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.core.parameter.parse_parameter import parse_parameter


def init(actionContext: ActionContext):
    def copy_to_memory():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "CopyToMemory"
        status.uid = actionContext.unitContext.stageContext.pipelineContext.pipeline.pipelineId

        current_data = actionContext.currentOfTriggerData
        pipeline_topic = actionContext.unitContext.stageContext.pipelineContext.pipelineTopic
        action = actionContext.action
        variables = get_variables(actionContext)

        value_ = parse_parameter(action.source, current_data, variables)
        set_variable(actionContext, action.variableName, value_)

        elapsed_time = time.time() - start
        status.complete_time = elapsed_time
        return status, []
    return copy_to_memory
