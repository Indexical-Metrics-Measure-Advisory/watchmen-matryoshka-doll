import logging
import time

from watchmen.pipeline.core.by.parse_on_parameter import parse_parameter_joint
from watchmen.pipeline.core.context.action_context import get_variables, set_variable
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.storage.read_topic_data import query_topic_data
from watchmen.pipeline.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

log = logging.getLogger("app." + __name__)


def init(actionContext):
    def read_factor():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "ReadFactor"
        status.uid = actionContext.unitContext.stageContext.pipelineContext.pipeline.pipelineId

        previous_data = actionContext.previousOfTriggerData
        current_data = actionContext.currentOfTriggerData
        action = actionContext.action

        pipeline_topic = actionContext.unitContext.stageContext.pipelineContext.pipelineTopic
        target_topic = get_topic_by_id(action.topicId)
        variables = get_variables(actionContext)

        where_ = parse_parameter_joint(action.by, current_data, variables, pipeline_topic, target_topic)
        status.whereConditions = where_

        target_factor = get_factor(action.factorId, target_topic)

        target_data = query_topic_data(where_, target_topic.name)
        if target_data is not None:
            if isinstance(target_data, list):
                raise ValueError("read factor action should just get one factor record")
            else:
                read_value = target_data[target_factor.name]
                set_variable(actionContext, action.variableName, read_value)
                status.value = read_value

        elapsed_time = time.time() - start
        status.complete_time = elapsed_time
        return status, []

    return read_factor
