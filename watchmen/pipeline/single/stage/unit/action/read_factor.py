from datetime import datetime

from watchmen.monitor.model.pipeline_monitor import UnitStatus, ReadFactorAction
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.action.insert_or_merge_row import filter_condition
from watchmen.pipeline.single.stage.unit.mongo.index import build_right_query
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor, get_execute_time
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
        start_time = datetime.now()
        context_target_name = action.targetName
        topic = get_topic_by_id(action.topicId)
        factor = get_factor(action.factorId, topic)
        condition = action.by
        where_condition = build_right_query(condition, pipeline_topic, raw_data, topic)
        filter_where_condition = filter_condition(where_condition, 0)
        target_data = read_topic_data(filter_where_condition, topic.name, condition.mode)
        if factor.name in target_data:
            read_value = target_data[factor.name]
            context[context_target_name] = target_data[factor.name]

            # build log action
            build_action_log(factor, read_value, topic, unit_action_status)

        unit_action_status.complete_time = get_execute_time(start_time)
        return context, unit_action_status

    return read_factor
