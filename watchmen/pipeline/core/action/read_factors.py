import logging
import time

from watchmen.pipeline.core.by.parse_on_parameter import parse_parameter_joint
from watchmen.pipeline.core.context.action_context import ActionContext, get_variables, set_variable
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.storage.read_topic_data import query_multiple_topic_data
from watchmen.pipeline.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

log = logging.getLogger("app." + __name__)


def init(action_context: ActionContext):
    def read_factors():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "read-factors"
        status.uid = action_context.unitContext.stageContext.pipelineContext.pipeline.pipelineId

        previous_data = action_context.previousOfTriggerData
        current_data = action_context.currentOfTriggerData
        action = action_context.action

        pipeline_topic = action_context.unitContext.stageContext.pipelineContext.pipelineTopic
        target_topic = get_topic_by_id(action.topicId)
        variables = get_variables(action_context)

        where_ = parse_parameter_joint(action.by, current_data, variables, pipeline_topic, target_topic)
        status.by = where_

        target_factor = get_factor(action.factorId, target_topic)

        target_data = query_multiple_topic_data(where_, target_topic,
                                                action_context.get_current_user())

        if target_data is not None:
            if isinstance(target_data, list):
                factor_value_list = []
                for item_ in target_data:
                    read_value = item_[target_factor.name]
                    factor_value_list.append(read_value)
                set_variable(action_context, action.variableName, factor_value_list)
                status.value = factor_value_list
            else:
                read_value = target_data[target_factor.name]
                set_variable(action_context, action.variableName, [read_value])
                status.value = read_value
        else:
            raise ValueError("read factors action must match one factor record at least")
        status.completeTime = time.time() - start
        return status, []

    return read_factors
