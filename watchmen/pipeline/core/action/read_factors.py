import logging
import time

from watchmen.pipeline.core.by.parse_on_parameter import parse_parameter_joint
from watchmen.pipeline.core.context.action_context import ActionContext, get_variables, set_variable
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import query_multiple_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

log = logging.getLogger("app." + __name__)


def __check_factors_result(target_data_list):
    if isinstance(target_data_list, list):
        pass
    else:
        log.warning("result is not a list {0}".format(target_data_list))


def init(actionContext: ActionContext):
    def read_factors():
        # begin time
        start = time.time()

        # create action status monitor
        status = ActionStatus()
        status.type = "ReadFactors"
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

        # target_data = query_topic_data(where_, target_topic.name)
        target_data = query_multiple_topic_data(where_, target_topic.name)

        if target_data is not None:
            if isinstance(target_data, list):
                factor_value_list = []
                for item_ in target_data:
                    read_value = item_[target_factor.name]
                    factor_value_list.append(read_value)
                set_variable(actionContext, action.variableName, factor_value_list)
                status.value = factor_value_list
            else:
                read_value = target_data[target_factor.name]
                set_variable(actionContext, action.variableName, [read_value])
                status.value = read_value

        status.complete_time = time.time() - start
        return status, []

    return read_factors
