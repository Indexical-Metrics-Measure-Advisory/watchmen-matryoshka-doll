from datetime import datetime

from watchmen.monitor.model.pipeline_monitor import UnitStatus
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import run_mapping_rules, \
    build_right_query
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import insert_topic_data, update_topic_data

from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic


def filter_condition(where_condition, index):
    filter_conditions = []
    for condition in where_condition:
        filter_condition = {"name": condition["name"], "operator": condition["operator"]}
        if type(condition["value"]) is list:
            filter_condition["value"] = condition["value"][index]
        else:
            filter_condition["value"] = condition["value"]

        filter_conditions.append(filter_condition)
    return filter_conditions


def init(action: UnitAction, pipeline_topic: Topic):
    def merge_or_insert_topic(raw_data, context):

        unit_action_status = UnitStatus()
        unit_action_status.type = action.type
        start_time = datetime.now()

        if action.topicId is not None:
            target_topic = get_topic_by_id(action.topicId)
            mapping_results = run_mapping_rules(action.mapping, target_topic, raw_data, pipeline_topic)
            condition = action.by
            where_condition = build_right_query(condition, pipeline_topic, raw_data, target_topic)
            for index in range(len(mapping_results)):
                filter_where_condition = filter_condition(where_condition, index)
                # print("filter_where_condition:", filter_where_condition)
                target_data = read_topic_data(filter_where_condition, target_topic.name, condition.jointType)
                # print("target: ", target_data)
                if target_data is None:
                    insert_topic_data(target_topic.name, mapping_results[index])
                else:
                    update_topic_data(target_topic.name, mapping_results[index], target_data)
        time_elapsed = datetime.now() - start_time
        execution_time = time_elapsed.microseconds / 1000
        unit_action_status.complete_time = execution_time
        return context, unit_action_status

    return merge_or_insert_topic
