import time

from watchmen.pipeline.core.by.parse_on_parameter import parse_parameter_joint
from watchmen.pipeline.core.context.action_context import ActionContext, get_variables, set_variable
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.storage.read_topic_data import query_topic_data
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def init(action_context: ActionContext):
    def exists():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "Exists"
        status.uid = action_context.get_pipeline_id()

        previous_data = action_context.previousOfTriggerData
        current_data = action_context.currentOfTriggerData
        action = action_context.action
        pipeline_topic = action_context.get_pipeline_context().pipelineTopic
        target_topic = get_topic_by_id(action.topicId)
        variables = get_variables(action_context)

        where_ = parse_parameter_joint(action.by, current_data, variables, pipeline_topic, target_topic)
        status.whereConditions = where_

        target_data = query_topic_data(where_,
                                       target_topic, action_context.get_current_user())

        if target_data is not None:
            set_variable(action_context, action.variableName, 'true')
        else:
            set_variable(action_context, action.variableName, 'false')

        elapsed_time = time.time() - start
        status.completeTime = elapsed_time
        return status, []

    return exists
