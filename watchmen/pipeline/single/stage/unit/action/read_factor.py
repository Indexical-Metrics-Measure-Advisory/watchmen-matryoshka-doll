import logging
import time

from watchmen.common.constants import pipeline_constants
from watchmen.monitor.model.pipeline_monitor import ReadFactorAction
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import process_variable, build_query_conditions, \
    __build_mongo_query
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import query_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor, convert_factor_type
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


def init(action: UnitAction, pipeline_topic: Topic):
    def read_factor(instance, context):
        raw_data, old_value = instance[pipeline_constants.NEW], instance[pipeline_constants.OLD]
        unit_action_status = ReadFactorAction(type=action.type)
        start = time.time()
        # print("context",context)
        variable_type, context_target_name = process_variable(action.variableName)
        topic = get_topic_by_id(action.topicId)
        factor = get_factor(action.factorId, topic)
        joint_type, where_condition = build_query_conditions(action.by, pipeline_topic, raw_data, topic, context)
        mongo_query = __build_mongo_query(joint_type, where_condition)
        # print("mongo_query",mongo_query)
        target_data = query_topic_data(mongo_query, topic.name)
        if target_data is not None:
            if factor.name in target_data:
                read_value = target_data[factor.name]
                context[context_target_name] = target_data[factor.name]
                unit_action_status.value = read_value
        else:
            context[context_target_name] = convert_factor_type(factor.defaultValue,factor.type)
            log.warn("target_data is empty ,conditions {0}".format(mongo_query))

        elapsed_time = time.time() - start
        unit_action_status.complete_time = elapsed_time
        # print("read context",context)
        return context, unit_action_status,[]

    return read_factor
