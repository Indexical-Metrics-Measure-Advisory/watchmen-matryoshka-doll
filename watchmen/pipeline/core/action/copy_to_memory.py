import time

from watchmen.pipeline.core.context.action_context import ActionContext, set_variable, get_variables
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.core.parameter.parse_parameter import parse_parameter


def init(action_context: ActionContext):
    def copy_to_memory():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "copy-to-memory"
        status.uid = action_context.get_pipeline_id()

        current_data = action_context.currentOfTriggerData
        pipeline_topic = action_context.unitContext.stageContext.pipelineContext.pipelineTopic
        action = action_context.action
        variables = get_variables(action_context)

        value_ = parse_parameter(action.source, current_data, variables)
        set_variable(action_context, action.variableName, value_)

        elapsed_time = time.time() - start
        status.completeTime = elapsed_time
        return status, []

    return copy_to_memory
