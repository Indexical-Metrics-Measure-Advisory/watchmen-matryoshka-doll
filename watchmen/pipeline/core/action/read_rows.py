import time

from watchmen.pipeline.core.by.parse_on_parameter import parse_parameter_joint
from watchmen.pipeline.core.context.action_context import ActionContext, set_variable, get_variables
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.storage.read_topic_data import query_topic_data, query_multiple_topic_data
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def init(action_context: ActionContext):
    def read_rows():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "ReadRows"
        status.uid = action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId

        previous_data = action_context.previousOfTriggerData
        current_data = action_context.currentOfTriggerData
        action = action_context.action

        target_topic = get_topic_by_id(action.topicId)
        pipeline_topic = action_context.unitContext.stageContext.pipelineContext.pipelineTopic
        variables = get_variables(action_context)

        where_ = parse_parameter_joint(action.by, current_data, variables, pipeline_topic, target_topic)
        status.whereConditions = where_

        target_data = query_multiple_topic_data(where_, target_topic.name)

        if target_data is not None:
            if isinstance(target_data, list):
                set_variable(action_context, action.variableName, target_data)
                status.value = target_data
            else:
                set_variable(action_context, action.variableName, [target_data])
                status.value = target_data

        elapsed_time = time.time() - start
        status.complete_time = elapsed_time
        return status, []

    return read_rows
