import time

from watchmen.monitor.model.pipeline_monitor import UnitStatus, ReadFactorAction
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.action.insert_or_merge_row import filter_condition
from watchmen.pipeline.single.stage.unit.mongo.index import find_pipeline_topic_condition, \
    process_variable
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic


def build_action_log(factor, read_value, topic, unit_action_status):
    action_log = ReadFactorAction()
    action_log.value = read_value
    action_log.fromFactor = factor.name
    action_log.fromTopic = topic.name
    unit_action_status.actions.append(action_log)


def init(action: UnitAction, pipeline_topic: Topic):
    def read_factor(raw_data, context):
        unit_action_status = UnitStatus()
        unit_action_status.type = action.type
        start = time.time()
        variable_type, context_target_name = process_variable(action.variableName)

        topic = get_topic_by_id(action.topicId)
        factor = get_factor(action.factorId, topic)
        conditions = action.by
        where_condition = find_pipeline_topic_condition(conditions, pipeline_topic, raw_data, topic)
        filter_where_condition = filter_condition(where_condition)
        target_data = read_topic_data(filter_where_condition, topic.name,
                                      conditions.jointType)
        # print("target_data",target_data)
        if factor.name in target_data:
            read_value = target_data[factor.name]
            context[context_target_name] = target_data[factor.name]

            # build log action
            build_action_log(factor, read_value, topic, unit_action_status)
        elapsed_time = time.time() - start
        unit_action_status.complete_time = elapsed_time
        # print("context",context)
        return context, unit_action_status

    return read_factor
