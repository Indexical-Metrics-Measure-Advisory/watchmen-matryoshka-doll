import time

from watchmen.common.constants import pipeline_constants
from watchmen.monitor.model.pipeline_monitor import ReadFactorAction
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import process_variable, build_query_conditions, \
    __build_mongo_query
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import query_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic


def init(action: UnitAction, pipeline_topic: Topic):
    def read_factor(instance, context):
        raw_data, old_value = instance[pipeline_constants.NEW], instance[pipeline_constants.OLD]
        unit_action_status = ReadFactorAction(type=action.type)
        start = time.time()

        variable_type, context_target_name = process_variable(action.variableName)
        topic = get_topic_by_id(action.topicId)
        factor = get_factor(action.factorId, topic)
        joint_type, where_condition = build_query_conditions(action.by, pipeline_topic, raw_data, topic, context)
        mongo_query = __build_mongo_query(joint_type, where_condition)
        target_data = query_topic_data(mongo_query, topic.name)

        if factor.name in target_data:
            read_value = target_data[factor.name]
            context[context_target_name] = target_data[factor.name]
            unit_action_status.value = read_value
            # build_action_log(factor, read_value, topic, unit_action_status)
        elapsed_time = time.time() - start
        unit_action_status.complete_time = elapsed_time
        return context, unit_action_status

    return read_factor
