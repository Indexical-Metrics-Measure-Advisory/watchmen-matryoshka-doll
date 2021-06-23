import time

from watchmen.pipeline.core.by.parse_on_parameter import parse_parameter_joint
from watchmen.pipeline.core.context.action_context import ActionContext, get_variables, set_variable
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import query_topic_data
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def init(actionContext: ActionContext):
    def exists():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "Exists"
        status.uid = actionContext.unitContext.stageContext.pipelineContext.pipeline.pipelineId

        previous_data = actionContext.previousOfTriggerData
        current_data = actionContext.currentOfTriggerData
        action = actionContext.action
        pipeline_topic = actionContext.unitContext.stageContext.pipelineContext.pipelineTopic
        target_topic = get_topic_by_id(action.topicId)
        variables = get_variables(actionContext)

        where_ = parse_parameter_joint(action.by, current_data, variables, pipeline_topic, target_topic)
        status.whereConditions = where_

        target_data = query_topic_data(where_,
                                       target_topic.name)

        if target_data is not None:
            set_variable(actionContext, action.variableName, 'true')
        else:
            set_variable(actionContext, action.variableName, 'false')

        elapsed_time = time.time() - start
        status.complete_time = elapsed_time
        return status, []
    return exists
