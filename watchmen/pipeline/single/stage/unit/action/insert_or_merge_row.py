from watchmen.pipeline.model.pipeline import UnitAction, CompositeCondition
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import insert_topic_data, update_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_value, get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic


def get_target_data(condition: CompositeCondition, target_topic, pipeline_topic, raw_data):
    where_condition = build_right_query(condition, pipeline_topic, raw_data, target_topic)
    target_data = read_topic_data(where_condition, target_topic.name, condition.mode)
    return target_data


def build_right_query(condition, pipeline_topic, raw_data, target_topic):
    where_condition = []
    for sub_condition in condition.children:
        right_factor = get_factor(sub_condition.right.factorId, pipeline_topic)
        left_factor = get_factor(sub_condition.left.factorId, target_topic)
        right_value = get_value(right_factor, raw_data)
        where_condition.append({"name": left_factor.name, "value": right_value, "operator": sub_condition.operator})
        # left_value = get_value(sub_condition.left,target_topic_data,target_topic)
    return where_condition


def run_mapping_rules(mapping_list, target_topic, raw_data, pipeline_topic):
    mapping_result = {}
    for mapping in mapping_list:
        source = mapping["from"]
        source_factor = get_factor(source["factorId"], pipeline_topic)
        source_value = get_value(source_factor, raw_data)
        target = mapping["to"]
        target_factor = get_factor(target["factorId"], target_topic)
        ## TODO func convert
        mapping_result[target_factor.name]=source_value
    return mapping_result


def init(action: UnitAction, pipeline_topic: Topic):
    def merge_topic(raw_data):
        print("action:", action)
        if action.topicId is not None:
            target_topic = get_topic_by_id(action.topicId)
            condition = action.by
            data = get_target_data(condition, target_topic, pipeline_topic, raw_data)
            mapping_list = action.mapping
            mapping_result = run_mapping_rules(mapping_list, target_topic, raw_data, pipeline_topic)
            if data is None:
                insert_topic_data(target_topic.name, mapping_result)
            else:
                update_topic_data(target_topic.name, mapping_result,data)

    return merge_topic
