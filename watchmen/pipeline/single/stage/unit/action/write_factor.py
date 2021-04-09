import logging
import time

from watchmen.common.constants import pipeline_constants
from watchmen.monitor.model.pipeline_monitor import WriteFactorAction
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import build_query_conditions, get_source_value_list, \
    __build_mongo_query, __build_mongo_update
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import find_and_modify_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor, get_value
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


def get_condition_factor_value(raw_data, where_conditions, joint_type):
    if joint_type is None:
        return {where_conditions[pipeline_constants.NAME].name: where_conditions[pipeline_constants.VALUE]}
    else:
        factor_value = {}
        for condition in where_conditions:
            source_factor = condition[pipeline_constants.NAME]
            value = get_value(source_factor, raw_data)
            factor_value[source_factor.name] = value

        return factor_value


def __merge_condition_factor(update_data, condition_factors):
    return {**update_data, **condition_factors}


def init(action: UnitAction, pipeline_topic: Topic):
    def write_factor(instance, context):
        raw_data, old_value = instance[pipeline_constants.NEW], instance[pipeline_constants.OLD]
        unit_action_status = WriteFactorAction(type=action.type)
        start = time.time()
        # pipeline_uid = context[PIPELINE_UID]

        if action.topicId is not None:
            target_topic = get_topic_by_id(action.topicId)
            # todo for find factor
            # factor_dict = build_factor_dict(target_topic)
            conditions = action.by
            joint_type, where_condition = build_query_conditions(conditions, pipeline_topic, raw_data, target_topic,
                                                                 context)
            target_factor = get_factor(action.factorId, target_topic)
            source_value_list = get_source_value_list(pipeline_topic, raw_data, action.source,target_factor)

            update_data = {target_factor.name: source_value_list}
            mongo_query = __build_mongo_query(joint_type, where_condition)
            condition_factors = {"$set": get_condition_factor_value(raw_data, where_condition, joint_type)}
            if old_value is not None:
                old_value_list = get_source_value_list(pipeline_topic, old_value, action.source,target_factor)
                find_and_modify_topic_data(target_topic.name,
                                           mongo_query,
                                           __merge_condition_factor(
                                               __build_mongo_update(update_data, action.arithmetic, target_factor,
                                                                    old_value_list), condition_factors))
            else:
                find_and_modify_topic_data(target_topic.name,
                                           mongo_query,
                                           __merge_condition_factor(
                                               __build_mongo_update(update_data, action.arithmetic, target_factor),
                                               condition_factors))

        elapsed_time = time.time() - start
        unit_action_status.complete_time = elapsed_time
        return context, unit_action_status

    return write_factor
