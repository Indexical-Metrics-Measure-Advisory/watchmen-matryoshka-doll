import logging
import time

from watchmen.common.constants import pipeline_constants
from watchmen.monitor.model.pipeline_monitor import ReadFactorAction
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import process_variable, build_query_conditions, \
    __build_mongo_query
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import query_multiple_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor, convert_factor_type
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


def __check_factors_result(target_data_list):
    if isinstance(target_data_list, list):
        pass
    else:
        log.warning("result is not a list {0}".format(target_data_list))


def init(action: UnitAction, pipeline_topic: Topic):
    def read_factors(instance, context):
        raw_data, old_value = instance[pipeline_constants.NEW], instance[pipeline_constants.OLD]
        unit_action_status = ReadFactorAction(type=action.type)
        start = time.time()
        variable_type, context_target_name = process_variable(action.variableName)
        topic = get_topic_by_id(action.topicId)
        factor = get_factor(action.factorId, topic)
        joint_type, where_condition = build_query_conditions(action.by, pipeline_topic, raw_data, topic, context)
        mongo_query = __build_mongo_query(joint_type, where_condition)
        target_data_list = query_multiple_topic_data(mongo_query, topic.name)
        __check_factors_result(target_data_list)
        if target_data_list is not None:
            result_list = []
            for item in target_data_list:
                if factor.name in item:
                    read_value = item[factor.name]
                    result_list.append(read_value)
            context[context_target_name] = result_list
            unit_action_status.value = result_list
        else:
            context[context_target_name] = convert_factor_type(factor.defaultValue, factor.type)
            log.warning("target_data is empty ,conditions {0}".format(mongo_query))

        unit_action_status.complete_time = time.time() - start
        return context, unit_action_status, []

    return read_factors
