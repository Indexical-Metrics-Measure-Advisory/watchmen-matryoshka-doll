import logging
import time
from decimal import Decimal

from watchmen.common.utils.data_utils import get_id_name_by_datasource
from watchmen.database.datasource.container import data_source_container
from watchmen.pipeline.core.by.parse_on_parameter import parse_parameter_joint
from watchmen.pipeline.core.context.action_context import ActionContext, get_variables
from watchmen.pipeline.core.monitor.model.pipeline_monitor import ActionStatus
from watchmen.pipeline.core.parameter.parse_parameter import parse_parameter
from watchmen.pipeline.core.parameter.utils import check_and_convert_value_by_factor
from watchmen.pipeline.storage.read_topic_data import query_topic_data
from watchmen.pipeline.storage.write_topic_data import update_topic_data_one
from watchmen.pipeline.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

log = logging.getLogger("app." + __name__)


def init(action_context: ActionContext):
    def write_factor():

        start = time.time()
        # create action status monitor
        status = ActionStatus()
        status.type = "WriteFactor"
        status.uid = action_context.get_pipeline_id()

        previous_data = action_context.previousOfTriggerData
        current_data = action_context.currentOfTriggerData

        action = action_context.action

        if action.topicId is not None:

            pipeline_topic = action_context.get_pipeline_context().pipelineTopic
            target_topic = get_topic_by_id(action.topicId)
            variables = get_variables(action_context)

            where_ = parse_parameter_joint(action.by, current_data, variables, pipeline_topic, target_topic)
            status.whereConditions = where_

            target_data = query_topic_data(where_,
                                           target_topic,action_context.get_current_user())

            target_factor = get_factor(action.factorId, target_topic)
            source_ = action.source
            arithmetic = action.arithmetic

            result = None
            current_value_ = check_and_convert_value_by_factor(target_factor,
                                                               parse_parameter(source_, current_data, variables))
            if arithmetic is None or arithmetic == "none":  # mean AS IS
                result = {target_factor.name: current_value_}
            elif arithmetic == "sum":
                previous_value_ = check_and_convert_value_by_factor(target_factor,
                                                                    parse_parameter(source_, previous_data, variables))
                if previous_value_ is None:
                    previous_value_ = 0
                value_ = Decimal(current_value_) - Decimal(previous_value_)
                result = {target_factor.name: {"_sum": value_}}
            elif arithmetic == "count":
                if previous_data is None:
                    result = {target_factor.name: {"_count": 1}}
                else:
                    result = {target_factor.name: {"_count": 0}}
            elif arithmetic == "avg":
                result = {target_factor.name: {"_avg": current_value_}}

            updates_ = result
            trigger_pipeline_data_list = []
            if target_data is not None:
                trigger_pipeline_data_list.append(update_topic_data_one(
                    updates_, target_data,
                    action_context.get_pipeline_id(),
                    target_data[get_id_name_by_datasource(data_source_container.get_data_source_by_id(target_topic.dataSourceId))],
                    target_topic,action_context.get_current_user()))

        elapsed_time = time.time() - start
        status.complete_time = elapsed_time
        return status, trigger_pipeline_data_list

    return write_factor
