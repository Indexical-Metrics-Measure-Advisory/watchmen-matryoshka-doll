import logging

from watchmen.pipeline.model.pipeline import UnitAction
from watchmen.pipeline.single.stage.unit.action.insert_or_merge_row import build_right_query, filter_condition
from watchmen.pipeline.single.stage.unit.mongo.read_topic_data import read_topic_data
from watchmen.pipeline.single.stage.unit.mongo.write_topic_data import update_topic_data, insert_topic_data
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor, get_value, convert_factor_type
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


def get_condition_factor_value(raw_data, where_conditions):
    factor_value = {}
    for condition in where_conditions:
        right_factor = condition["right_factor"]
        value = get_value(right_factor, raw_data)

        factor_value[right_factor.name] = value

    return factor_value


def init(action: UnitAction, pipeline_topic: Topic):
    def write_factor(raw_data, context):

        if action.topicId is not None:

            print("raw_data",raw_data)
            target_topic = get_topic_by_id(action.topicId)

            condition = action.by

            some_value = action.value
            where_condition = build_right_query(condition, pipeline_topic, raw_data, target_topic)
            filter_where_condition = filter_condition(where_condition, 0)
            target_data = read_topic_data(filter_where_condition, target_topic.name, condition.mode)

            print("target_data :",target_data)

            target_factor = get_factor(action.factorId, target_topic)

            value = __get_value(raw_data, some_value, context, target_factor)
            condition_factors = get_condition_factor_value(raw_data, where_condition)

            if some_value.arithmetic == "sum":
                if target_data is None:
                    insert_data = {**{target_factor.name: value}, **condition_factors}
                    log.info("Insert data : {0}".format(insert_data))
                    insert_topic_data(target_topic.name, insert_data)
                else:
                    print("target_factor.name :",target_factor.name)
                    if target_factor.name in target_data:
                        source_value = target_data[target_factor.name]
                    else:
                        source_value = 0
                    value = source_value + value
                    update_data = {target_factor.name: value}
                    update_topic_data(target_topic.name, update_data, target_data)
            # target_data = read_topic_data(filter_where_condition, target_topic.name, condition.mode)
            elif some_value.arithmetic == "count":
                if target_data is None:
                    insert_data = {**{target_factor.name: 1}, **condition_factors}
                    insert_topic_data(target_topic.name, insert_data)
                else:
                    if target_factor.name in target_data:
                        source_value = target_data[target_factor.name]
                    else:
                        source_value = 0
                    value = source_value + 1
                    update_data = {target_factor.name: value}
                    update_topic_data(target_topic.name, update_data, target_data)
            else:
                if target_data is None:
                    insert_data = {**{target_factor.name: value}, **condition_factors}
                    log.debug("Insert data : {0}".format(insert_data))
                    insert_topic_data(target_topic.name, insert_data)
                else:
                    update_data = {target_factor.name: value}
                    update_topic_data(target_topic.name, update_data, target_data)

        return context

    def __get_value(raw_data, some_value, context, target_factor):
        if some_value.type == "in-memory":
            return convert_factor_type(context[some_value.name], target_factor.type)
        else:
            source_factor = get_factor(some_value.factorId, pipeline_topic)
            value = get_value(source_factor, raw_data)
            return value

    return write_factor
