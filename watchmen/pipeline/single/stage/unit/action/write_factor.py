from watchmen.pipeline.single.stage.unit.action.insert_or_merge_row import build_right_query, filter_condition
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import update_topic_data, insert_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor, get_value
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.topic.topic import Topic


def get_condition_factor_value( raw_data, where_conditions):
    factor_value={}
    for condition in where_conditions:
        right_factor =condition["right_factor"]
        value =get_value(right_factor,raw_data)

        factor_value[right_factor.name]=value

    return factor_value


def init(action: UnitAction, pipeline_topic: Topic):
    def write_factor(raw_data):
        print("write_factor in :", raw_data)
        if action.topicId is not None:
            target_topic = get_topic_by_id(action.topicId)

            condition = action.by

            some_value = action.value
            where_condition = build_right_query(condition, pipeline_topic, raw_data, target_topic)
            filter_where_condition = filter_condition(where_condition, 0)
            target_data = read_topic_data(filter_where_condition, target_topic.name, condition.mode)
            source_factor = get_factor(some_value.factorId, pipeline_topic)
            target_factor = get_factor(action.factorId, target_topic)
            value = get_value(source_factor, raw_data)
            condition_factors =get_condition_factor_value(raw_data,where_condition)

            if some_value.arithmetic == "sum":
                if target_data is None:
                    # insert_data = |condition_factors

                    insert_data = {**{target_factor.name: value}, **condition_factors}
                    # print
                    insert_topic_data(target_topic.name,insert_data)
                else:
                    if target_factor.name in target_data:
                        source_value = target_data[target_factor.name]
                    else:
                        source_value = 0
                    value = source_value + value
                    update_data = {target_factor.name: value}
                    update_topic_data(target_topic.name, update_data, target_data)

            # target_data = read_topic_data(filter_where_condition, target_topic.name, condition.mode)
            if some_value.arithmetic == "count":
                if target_data is None:
                    insert_data = {**{target_factor.name: 1}, **condition_factors}
                    insert_topic_data(target_topic.name,insert_data)
                else:
                    if target_factor.name in target_data:
                        source_value = target_data[target_factor.name]
                    else:
                        source_value =0
                    value = source_value + 1
                    update_data = {target_factor.name: value}
                    update_topic_data(target_topic.name, update_data, target_data)

    return write_factor
