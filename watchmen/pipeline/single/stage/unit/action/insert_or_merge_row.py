from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.mongo.index import run_mapping_rules, get_source_factor_value
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import insert_topic_data, update_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic


def build_right_query(condition, pipeline_topic, raw_data, target_topic):
    where_condition = []
    for sub_condition in condition.children:
        right_factor = get_factor(sub_condition.right.factorId, pipeline_topic)
        left_factor = get_factor(sub_condition.left.factorId, target_topic)
        # right_value = get_value(right_factor, raw_data)
        right_value_list = get_source_factor_value(raw_data, [], right_factor)
        where_condition.append(
            {"name": left_factor.name, "value": right_value_list, "operator": sub_condition.operator,"right_factor": right_factor})
        # left_value = get_value(sub_condition.left,target_topic_data,target_topic)
    return where_condition


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
    def merge_or_insert_topic(raw_data):
        # print("action:", action)
        if action.topicId is not None:
            target_topic = get_topic_by_id(action.topicId)
            mapping_results = run_mapping_rules(action.mapping, target_topic, raw_data, pipeline_topic)
            condition = action.by
            where_condition = build_right_query(condition, pipeline_topic, raw_data, target_topic)
            for index in range(len(mapping_results)):
                filter_where_condition = filter_condition(where_condition, index)
                # print("filter_where_condition:", filter_where_condition)
                target_data = read_topic_data(filter_where_condition, target_topic.name, condition.mode)
                # print("target: ", target_data)
                if target_data is None:
                    insert_topic_data(target_topic.name, mapping_results[index])
                else:
                    update_topic_data(target_topic.name, mapping_results[index], target_data)

    return merge_or_insert_topic
