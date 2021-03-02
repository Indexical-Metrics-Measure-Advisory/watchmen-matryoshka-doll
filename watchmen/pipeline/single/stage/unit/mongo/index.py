import logging
import statistics
from datetime import datetime
from functools import reduce

import numpy as np
import pandas as pd

from watchmen.pipeline.model.pipeline import ParameterJoint, Parameter
from watchmen.pipeline.single.stage.unit.utils.units_func import get_value, get_factor
from watchmen.plugin.service.plugin_service import run_plugin
from watchmen.topic.factor.factor import Factor
from watchmen.topic.topic import Topic

DOT = "."

log = logging.getLogger("app." + __name__)

NONE = 'none'

YEAR_OF = 'year-of'
HALF_YEAR_OF = 'half-year-of'
QUARTER_OF = 'quarter-of'
MONTH_OF = 'month-of'
WEEK_OF_YEAR = 'week-of-year'
WEEK_OF_MONTH = 'week-of-month'
DAY_OF_MONTH = 'day-of-month'
DAY_OF_WEEK = 'weekdays'

ADD = 'add'
SUBTRACT = 'subtract'
MULTIPLY = 'multiply'
DIVIDE = 'divide'
MODULUS = 'modulus'

COUNT = 'count',
SUM = 'sum',
AVG = 'avg',
MAX = 'max',
MIN = 'min',
MEDIAN = 'med'

DATE_FUNC = [YEAR_OF, HALF_YEAR_OF, QUARTER_OF, MONTH_OF, WEEK_OF_YEAR, WEEK_OF_MONTH, DAY_OF_WEEK, DAY_OF_MONTH]

CALC_FUNC = [ADD, SUBTRACT, MULTIPLY, DIVIDE, MODULUS]


def build_factor_list(factor):
    factor_name_list = factor.name.split(".")
    factor_list = []
    for name in factor_name_list:
        factor = Factor()
        factor.name = name
        factor_list.append(factor)
    return factor_list


def __convert_value_to_datetime(value):
    if type(value) == datetime:
        return value
    else:
        return datetime.fromisoformat(value)


def __run_arithmetic(arithmetic, value):
    # print("value",value)
    if arithmetic == NONE:
        return value
    elif arithmetic == SUM:
        return sum(value)
    elif arithmetic == AVG:
        return statistics.mean(value)
    elif arithmetic == MAX:
        return statistics.max(value)
    elif arithmetic == MIN:
        return statistics.min(value)
    elif arithmetic == MEDIAN:
        return statistics.median(value)


def run_arithmetic_value_list(arithmetic, source_value_list):
    if type(source_value_list) == list:
        results = []
        for source_value in source_value_list:
            results.append(__run_arithmetic(arithmetic, source_value))
        return results
    else:
        return __run_arithmetic(arithmetic, source_value_list)


def __process_factor_type(target_factor, source_value_list):
    results = []
    if source_value_list is not None:
        if type(source_value_list) == list:
            for source_value in source_value_list:
                if source_value is not None:
                    result = run_plugin(target_factor.type, source_value)
                    if result is not None:
                        results.append(result)
            return results
        else:
            return run_plugin(target_factor.type, source_value_list)


def run_mapping_rules(mapping_list, target_topic, raw_data, pipeline_topic):
    mapping_logs = []

    mapping_results = []

    for mapping in mapping_list:
        mapping_log = {}
        source = mapping.source

        mapping_log["source"] = source

        mapping_log["arithmetic"] = mapping.arithmetic
        result = []
        source_value_list = run_arithmetic_value_list(mapping.arithmetic,
                                                      get_source_value_list(pipeline_topic, raw_data, result, source))

        mapping_log["value"] = source_value_list
        target_factor = get_factor(mapping.factorId, target_topic)

        mapping_log["target"] = target_factor
        # print("source_value_list", source_value_list)

        result = __process_factor_type(target_factor, source_value_list)
        merge_plugin_results(mapping_results, result)
        mapping_results.append({target_factor.name: source_value_list})

        mapping_logs.append(mapping_log)

    mapping_data_list = merge_mapping_data(mapping_results)
    return mapping_data_list, mapping_logs


def merge_plugin_results(mapping_results, result):
    if result is not None and len(result) > 0:
        mapping_results.append(result[0])


def __is_date_func(source_type):
    return source_type in DATE_FUNC


def __week_number_of_month(date_value):
    return date_value.isocalendar()[1] - date_value.replace(day=1).isocalendar()[1] + 1


def __process_date_func(source, value):
    log.info("value : {0}".format(value))
    arithmetic = source.type
    if arithmetic == NONE:
        return value
    elif arithmetic == YEAR_OF:
        return __convert_value_to_datetime(value).year
    elif arithmetic == MONTH_OF:
        return __convert_value_to_datetime(value).month
    elif arithmetic == WEEK_OF_YEAR:
        return __convert_value_to_datetime(value).isocalendar()[1]
    elif arithmetic == DAY_OF_WEEK:
        return __convert_value_to_datetime(value).weekday()
    elif arithmetic == WEEK_OF_MONTH:
        return __week_number_of_month(__convert_value_to_datetime(value).date())
    elif arithmetic == QUARTER_OF:
        quarter = pd.Timestamp(__convert_value_to_datetime(value)).quarter
        return quarter
    elif arithmetic == HALF_YEAR_OF:
        month = __convert_value_to_datetime(value).month
        if month <= 6:
            return 1
        else:
            return 2
    elif arithmetic == DAY_OF_MONTH:
        days_in_month = pd.Timestamp(__convert_value_to_datetime(value)).days_in_month
        return days_in_month
    else:
        raise ValueError("unknown arithmetic type {0}".format(arithmetic))


def __is_calculation_operation(source_type):
    return source_type in CALC_FUNC


def __get_operator(source_type):
    if source_type == ADD:
        return np.add
    elif source_type == SUBTRACT:
        return np.subtract
    elif source_type == MULTIPLY:
        return np.multiply
    elif source_type == DIVIDE:
        return np.divide
    elif source_type == MODULUS:
        return np.mod
    else:
        raise Exception("unknown source_type {0}".format(source_type))


def __process_operator(operator, value_list):
    return reduce(operator, value_list)


def __process_compute_kind(source: Parameter, raw_data, pipeline_topic):
    if __is_date_func(source.type):
        value_list = get_source_value_list(pipeline_topic, raw_data, [], Parameter.parse_obj(source.parameters[0]))
        if type(value_list) == list:
            result = []
            for value in value_list:
                result.append(__process_date_func(source, value))
            return result
        else:
            return
    elif __is_calculation_operation(source.type):
        operator = __get_operator(source.type)
        value_list = []
        for parameter in source.parameters:
            value = get_source_value_list(pipeline_topic, raw_data, [], Parameter.parse_obj(parameter))
            if type(value) is list:
                value_list.append(np.array(value))
            else:
                value_list.append(value)
        # print("value :", value_list)

        return __process_operator(operator, value_list).tolist()


def get_source_value_list(pipeline_topic, raw_data, result, parameter):
    if parameter.kind == "topic":
        source_factor: Factor = get_factor(parameter.factorId, pipeline_topic)
        return get_source_factor_value(raw_data, result, source_factor)
    elif parameter.kind == "constant":
        return parameter.value
    elif parameter.kind == "computed":
        return __process_compute_kind(parameter, raw_data, pipeline_topic)
    else:
        raise Exception("Unknown source kind {0}".format(parameter.kind))


def get_source_factor_value(raw_data, result, source_factor):
    if is_sub_field(source_factor):
        factor_list = build_factor_list(source_factor)
        source_value_list = get_factor_value(0, factor_list, raw_data, result)
    else:
        source_value_list = get_value(source_factor, raw_data)
    return source_value_list


def merge_mapping_data(mapping_results):
    max_value_size = get_max_value_size(mapping_results)
    mapping_data_list = []
    for i in range(max_value_size):
        mapping_data = {}
        for mapping_result in mapping_results:
            for key, value in mapping_result.items():
                if type(value) is list and len(value) > 0:
                    mapping_data[key] = value[i]
                else:
                    mapping_data[key] = value
        mapping_data_list.append(mapping_data)
    return mapping_data_list


def get_max_value_size(mapping_results):
    index = 0
    for mapping_result in mapping_results:
        for key, value in mapping_result.items():
            if type(value) is list:
                # index = len(value)
                if len(value) > index:
                    index = len(value)
            else:
                index = 1
    return index


def __process_parameter_join(parameter_join: ParameterJoint):
    if parameter_join.jointType == "and":
        pass
    elif parameter_join.jointType == "or":
        pass
    else:
        raise Exception("unknown parameter join type {0}".format(parameter_join.jointType))


def build_right_query(condition, pipeline_topic, raw_data, target_topic):
    where_condition = []
    for sub_condition in condition.filters:
        right_factor = get_factor(sub_condition.right.factorId, pipeline_topic)
        left_factor = get_factor(sub_condition.left.factorId, target_topic)
        right_value_list = get_source_factor_value(raw_data, [], right_factor)
        where_condition.append(
            {"name": left_factor.name, "value": right_value_list, "operator": sub_condition.operator,
             "right_factor": right_factor})
        # left_value = get_value(sub_condition.left,target_topic_data,target_topic)
    return where_condition


def is_sub_field(factor):
    return DOT in factor.name


def get_factor_value(index, factor_list, raw_data, result):
    factor = factor_list[index]
    data = get_value(factor, raw_data)
    if type(data) is list:
        for raw in data:
            get_factor_value(index + 1, factor_list, raw, result)
    elif type(data) is dict:
        get_factor_value(index + 1, factor_list, data, result)
    else:
        result.append(data)
    return result


def filter_condition(where_condition, index=0):
    filter_conditions = []
    for condition in where_condition:
        filter_condition = {"name": condition["name"], "operator": condition["operator"]}
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
                 "source_factor": source_factor})

    return where_condition


# TODO operator for mongo
# TODO  jointType
def build_mongo_condition(where_condition, jointType):
    # print("where_condition",where_condition)
    result = {}
    if len(where_condition) > 1:
        for condition in where_condition:
            if condition["operator"] == "equals":
                name = condition["name"]
                value = condition["value"]
                result[name] = value
        return result
    else:
        condition = where_condition[0]
        if condition["operator"] == "equals":
            return {condition["name"]: condition["value"]}


def process_variable(variable_name):
    if variable_name.startswith("{"):
        return "memory", variable_name.replace("{", "").replace("}", "")
    else:
        return "constant", variable_name
