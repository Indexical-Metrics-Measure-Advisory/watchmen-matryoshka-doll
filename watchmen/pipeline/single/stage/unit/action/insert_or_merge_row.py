from datetime import datetime

from watchmen.common.parameter import ParameterJoint, Parameter
from watchmen.monitor.model.pipeline_monitor import UnitStatus
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import run_mapping_rules, \
    get_source_value_list
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import insert_topic_data, update_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_execute_time, get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic


def filter_condition(where_condition, index):
    filter_conditions = []
    for condition in where_condition:
        filter_condition = {"name": condition["source_factor"], "operator": condition["operator"]}
        if type(condition["value"]) is list:
            filter_condition["value"] = condition["value"][index]
        else:
            filter_condition["value"] = condition["value"]

        filter_conditions.append(filter_condition)

    return filter_conditions


def __is_pipeline_topic(parameter: Parameter, pipeline_topic: Topic):
    if parameter.kind == "topic" and parameter.topicId == pipeline_topic.topicId:
        return True
    else:
        return False


def __get_source_and_target_parameter(condition, pipeline_topic: Topic):
    if __is_pipeline_topic(condition.left, pipeline_topic):
        return condition.left, condition.right
    elif __is_pipeline_topic(condition.right, pipeline_topic):
        return condition.right, condition.left
    else:
        return None, None


def find_pipeline_topic_condition(conditions: ParameterJoint, pipeline_topic, raw_data, target_topic):
    where_condition = []
    for condition in conditions.filters:
        source_parameter, target_parameter = __get_source_and_target_parameter(condition, pipeline_topic)
        if source_parameter is None:
            # TODO constant value
            pass
        else:
            source_factor = get_factor(source_parameter.factorId, pipeline_topic)
            value_list = get_source_value_list(pipeline_topic, raw_data, [], source_parameter)
            target_factor = get_factor(target_parameter.factorId, target_topic)
            where_condition.append(
                {"name": target_factor.name, "value": value_list, "operator": condition.operator,
                 "source_factor": source_factor.name})

    return where_condition


def init(action: UnitAction, pipeline_topic: Topic):
    def merge_or_insert_topic(raw_data, context):

        unit_action_status = UnitStatus()
        unit_action_status.type = action.type
        start_time = datetime.now()

        if action.topicId is None:
            raise ValueError("action.topicId is empty {0}".format(action.name))

        target_topic = get_topic_by_id(action.topicId)

        mapping_results = run_mapping_rules(action.mapping, target_topic, raw_data, pipeline_topic)

        conditions = action.by

        where_condition = find_pipeline_topic_condition(conditions, pipeline_topic, raw_data, target_topic)

        for index in range(len(mapping_results)):
            filter_where_condition = filter_condition(where_condition, index)

            target_data = read_topic_data(filter_where_condition, target_topic.name, conditions.jointType)
            if target_data is None:
                insert_topic_data(target_topic.name, mapping_results[index])
            else:
                update_topic_data(target_topic.name, mapping_results[index], target_data)

        unit_action_status.complete_time = get_execute_time(start_time)
        return context, unit_action_status

    return merge_or_insert_topic
