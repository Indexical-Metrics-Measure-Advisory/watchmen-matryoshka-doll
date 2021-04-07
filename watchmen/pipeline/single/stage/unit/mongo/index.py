import logging
import statistics
from datetime import datetime
from decimal import Decimal
from functools import reduce

import numpy as np
import pandas as pd

from watchmen.common.constants import pipeline_constants, parameter_constants, mongo_constants
from watchmen.common.constants.pipeline_constants import VALUE
from watchmen.common.utils.condition_result import ConditionResult
from watchmen.config.config import settings
from watchmen.pipeline.model.pipeline import ParameterJoint, Parameter, Conditional
from watchmen.pipeline.single.stage.unit.utils.units_func import get_value, get_factor, process_variable, \
    check_condition
from watchmen.plugin.service.plugin_service import run_plugin
# from watchmen.routers.admin import DATE_FORMAT, DATE_FORMAT_2
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
DAY_OF_WEEK = 'day-of-week'

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
        return datetime.strptime(value,settings.TOPIC_DATE_FORMAT)


def __run_arithmetic(arithmetic, value):
    if arithmetic == NONE:
        return value
    elif arithmetic == SUM:
        return sum(value)
    elif arithmetic == AVG:
        return statistics.mean(value)
    elif arithmetic == MAX:
        return max(value)
    elif arithmetic == MIN:
        return min(value)
    elif arithmetic == MEDIAN:
        return statistics.median(value)


def run_arithmetic_value_list(arithmetic, value_list):

    print("value_list",value_list)
    if type(value_list) == list:
        results = []
        for source_value in value_list:
            results.append(__run_arithmetic(arithmetic, source_value))
        return results
    else:
        return __run_arithmetic(arithmetic, value_list)


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
    mapping_results = []

    for mapping in mapping_list:
        source = mapping.source
        source_value_list = run_arithmetic_value_list(mapping.arithmetic,
                                                      get_source_value_list(pipeline_topic, raw_data, source))

        print("source_value_list",source_value_list)
        target_factor = get_factor(mapping.factorId, target_topic)
        result = __process_factor_type(target_factor, source_value_list)
        merge_plugin_results(mapping_results, result)
        mapping_results.append({target_factor.name: source_value_list})

    mapping_data_list = merge_mapping_data(mapping_results)
    return mapping_data_list


def merge_plugin_results(mapping_results, result):
    if result is not None and len(result) > 0:
        mapping_results.append(result[0])


def __is_date_func(source_type):
    return source_type in DATE_FUNC


def __week_number_of_month(date_value):
    return date_value.isocalendar()[1] - date_value.replace(day=1).isocalendar()[1] + 1


def __process_date_func(source, value):
    log.info("source type {0}  value : {1}".format(source.type, value))

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
    result = reduce(operator, value_list)
    return result


def __process_compute_kind(source: Parameter, raw_data, pipeline_topic):
    if __is_date_func(source.type):
        value_list = get_source_value_list(pipeline_topic, raw_data, Parameter.parse_obj(source.parameters[0]))
        if type(value_list) == list:
            result = []
            for value in value_list:
                result.append(__process_date_func(source, value))
            return result
        else:
            return __process_date_func(source, value_list)
    elif __is_calculation_operation(source.type):
        operator = __get_operator(source.type)
        value_list = []
        for parameter in source.parameters:
            value = get_source_value_list(pipeline_topic, raw_data, Parameter.parse_obj(parameter))
            if type(value) is list:
                value_list.append(np.array(value))
            else:
                value_list.append(value)

        return __process_operator(operator, value_list)


def get_source_value_list(pipeline_topic, raw_data, parameter):
    if parameter.kind == parameter_constants.TOPIC:
        source_factor: Factor = get_factor(parameter.factorId, pipeline_topic)
        return get_source_factor_value(raw_data, source_factor)
    elif parameter.kind == parameter_constants.CONSTANT:
        if parameter.value is None or not parameter.value:
            return None
        else:
            return Decimal(parameter.value)
    elif parameter.kind == parameter_constants.COMPUTED:
        return __process_compute_kind(parameter, raw_data, pipeline_topic)
    else:
        raise Exception("Unknown source kind {0}".format(parameter.kind))


def get_source_factor_value(raw_data, source_factor):
    if is_sub_field(source_factor):
        factor_list = build_factor_list(source_factor)
        # print("factor_list",factor_list)
        source_value_list = get_factor_value(0, factor_list, raw_data, [])
    else:
        source_value_list = get_value(source_factor, raw_data)
    return source_value_list


def merge_mapping_data(mapping_results):
    max_value_size = get_max_value_size(mapping_results)
    mapping_data_list = []

    print("mapping_results",mapping_results)
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
                if len(value) > index:
                    index = len(value)
            else:
                index = 1
    return index


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


def __is_current_topic(parameter: Parameter, pipeline_topic: Topic):
    if parameter.kind == parameter_constants.TOPIC and parameter.topicId == pipeline_topic.topicId:
        return True
    else:
        return False


def __get_source_and_target_parameter(condition, pipeline_topic: Topic):
    if __is_current_topic(condition.left, pipeline_topic):
        return condition.left, condition.right
    elif __is_current_topic(condition.right, pipeline_topic):
        return condition.right, condition.left
    else:
        return None, None


def __process_parameter_constants(parameter: Parameter, context):
    variable_type, context_target_name = process_variable(parameter.value)
    if variable_type == parameter_constants.CONSTANT:
        # print("parameter",parameter.value)
        return Decimal(parameter.value)
    elif variable_type == parameter_constants.MEMORY:
        if context_target_name in context:
            return context[context_target_name]
        else:
            raise ValueError("no variable {0} in context".format(context_target_name))
    else:
        raise ValueError("variable_type is invalid")


def build_parameter_condition(parameter: Parameter, pipeline_topic: Topic, target_topic: Topic, raw_data, context):
    if parameter.kind == parameter_constants.TOPIC:
        if __is_current_topic(parameter, pipeline_topic):
            return {pipeline_constants.VALUE: get_source_value_list(pipeline_topic, raw_data, parameter)}
        elif __is_current_topic(parameter, target_topic):
            target_factor = get_factor(parameter.factorId, target_topic)
            return {pipeline_constants.NAME: target_factor}
    elif parameter.kind == parameter_constants.CONSTANT:
        return {pipeline_constants.VALUE: __process_parameter_constants(parameter, context)}
    elif parameter.kind == parameter_constants.COMPUTED:
        if __is_date_func(parameter.type):
            return {pipeline_constants.VALUE: __process_compute_date(parameter, pipeline_topic, raw_data)}
        elif __is_calculation_operation(parameter.type):
            return __process_compute_calculation_condition(parameter, pipeline_topic, target_topic, raw_data, context)
    else:
        raise Exception("Unknown parameter kind {0}".format(parameter.kind))


def __process_compute_calculation_condition(parameter, pipeline_topic, target_topic, raw_data, context):
    operator = __get_operator(parameter.type)
    value_list = []
    for parameter in parameter.parameters:
        parameter_result = build_parameter_condition(parameter, pipeline_topic, target_topic, raw_data, context)
        if pipeline_constants.VALUE in parameter_result:
            value = parameter_result[pipeline_constants.VALUE]
            if type(value) is list:
                value_list.append(np.array(value))
            else:
                value_list.append(value)
        if pipeline_constants.NAME in parameter_result:
            raise Exception("target_topic in compute parameter is not supported")

    return __process_operator(operator, value_list)


def __process_compute_date(parameter, pipeline_topic, raw_data):
    value_list = get_source_value_list(pipeline_topic, raw_data, Parameter.parse_obj(parameter.parameters[0]))
    if type(value_list) == list:
        result = []
        for value in value_list:
            result.append(__process_date_func(parameter, value))
        return result
    else:
        return __process_date_func(parameter, value_list)


def __process_condition(condition, pipeline_topic, target_topic, raw_data, context):
    where = {pipeline_constants.OPERATOR: condition.operator}
    process_parameter_result(build_parameter_condition(condition.left, pipeline_topic, target_topic, raw_data, context),
                             where)
    process_parameter_result(
        build_parameter_condition(condition.right, pipeline_topic, target_topic, raw_data, context), where)
    return where


def process_parameter_result(right_result, where):
    if pipeline_constants.NAME in right_result:
        where[pipeline_constants.NAME] = right_result[pipeline_constants.NAME]
    else:
        where[pipeline_constants.VALUE] = right_result[pipeline_constants.VALUE]


def build_query_conditions(conditions: ParameterJoint, pipeline_topic: Topic, raw_data, target_topic, context):
    if len(conditions.filters) == 1:
        # ignore jointType
        condition = conditions.filters[0]
        return None, __process_condition(condition, pipeline_topic, target_topic, raw_data, context)
    else:
        where_conditions = []
        for condition in conditions.filters:
            if condition.jointType is None:
                where_conditions.append(__process_condition(condition, pipeline_topic, target_topic, raw_data, context))
            else:
                where_conditions.append(
                    build_query_conditions(condition, pipeline_topic, target_topic, raw_data, context))

        return conditions.jointType, where_conditions


def __convert_to_list(value):
    if type(value) == list:
        return value
    else:
        # TODO for in and not in operator
        pass


def __build_on_condition(parameter_joint: ParameterJoint, topic, data):
    if parameter_joint.filters:
        joint_type = parameter_joint.jointType
        condition_result = ConditionResult(logicOperator=joint_type)
        for filter_condition in parameter_joint.filters:
            if filter_condition.jointType is not None:
                condition_result.resultList.append(__build_on_condition(filter_condition, topic, data))
            else:
                left_value_list = get_source_value_list(topic, data, filter_condition.left)
                right_value_list = get_source_value_list(topic, data, filter_condition.right)
                result: bool = check_condition(filter_condition.operator, left_value_list, right_value_list)
                condition_result.resultList.append(result)
        return condition_result


def __check_on_condition(match_result: ConditionResult) -> bool:
    if match_result is None or  match_result.logicOperator is None:
        return True
    elif match_result.logicOperator == "and":
        result = True
        for result in match_result.resultList:
            if type(result) == ConditionResult:
                if not __check_on_condition(result):
                    result = False
            else:
                if not result:
                    result = False
        return result
    elif match_result.logicOperator == "or":
        for result in match_result.resultList:
            if type(result) == ConditionResult:
                if __check_on_condition(result):
                    return True
            else:
                if result:
                    return True
    else:
        raise NotImplemented("not support {0}".format(match_result.logicOperator))


def __check_condition(condition_holder: Conditional, pipeline_topic, data):
    if condition_holder.conditional and condition_holder.on is not None:
        condition: ParameterJoint = condition_holder.on
        return __check_on_condition(__build_on_condition(condition, pipeline_topic, data[pipeline_constants.NEW]))
    else:
        return True


def __build_mongo_update(update_data, arithmetic, target_factor, old_value_list=None):
    # print("arithmetic",arithmetic)
    if arithmetic == "sum":
        if old_value_list is not None:
            dif_update_value = {target_factor.name: update_data[target_factor.name] - old_value_list}
            return {"$inc": dif_update_value}
        else:
            return {"$inc": update_data}
    elif arithmetic == "count":
        if old_value_list is not None:
            return {"$inc": {target_factor.name: 0}}
        else:
            return {"$inc": {target_factor.name: 1}}
    elif arithmetic == "max":
        return {"$max": update_data}
    elif arithmetic == "min":
        return {"$min": update_data}
    else:
        return update_data


def __process_where_condition(where_condition):
    if where_condition[pipeline_constants.OPERATOR] == parameter_constants.EQUALS:
        return {where_condition[pipeline_constants.NAME].name: where_condition[pipeline_constants.VALUE]}
    elif where_condition[pipeline_constants.OPERATOR] == parameter_constants.EMPTY:
        return {where_condition[pipeline_constants.NAME].name: None}
    elif where_condition[pipeline_constants.OPERATOR] == parameter_constants.NOT_EMPTY:
        return {where_condition[pipeline_constants.NAME].name: {"$exists": True}}
    elif where_condition[pipeline_constants.OPERATOR] == parameter_constants.NOT_EQUALS:
        return {where_condition[pipeline_constants.NAME].name: {"$ne": where_condition[pipeline_constants.VALUE]}}
    elif where_condition[pipeline_constants.OPERATOR] == parameter_constants.MORE:
        return {where_condition[pipeline_constants.NAME].name: {"$gt": where_condition[pipeline_constants.VALUE]}}
    elif where_condition[pipeline_constants.OPERATOR] == parameter_constants.LESS:
        return {where_condition[pipeline_constants.NAME].name: {"$lt": where_condition[pipeline_constants.VALUE]}}
    elif where_condition[pipeline_constants.OPERATOR] == parameter_constants.MORE_EQUALS:
        return {where_condition[pipeline_constants.NAME].name: {"$gte": where_condition[pipeline_constants.VALUE]}}
    elif where_condition[pipeline_constants.OPERATOR] == parameter_constants.LESS_EQUALS:
        return {where_condition[pipeline_constants.NAME].name: {"$lte": where_condition[pipeline_constants.VALUE]}}
    elif where_condition[pipeline_constants.OPERATOR] == parameter_constants.IN:
        return {where_condition[pipeline_constants.NAME].name: {
            "$in": __convert_to_list(where_condition[pipeline_constants.VALUE])}}
    elif where_condition[pipeline_constants.OPERATOR] == parameter_constants.IN:
        return {where_condition[pipeline_constants.NAME].name: {
            "$nin": __convert_to_list(where_condition[pipeline_constants.VALUE])}}


def index_conditions(where_condition, index):
    result = where_condition.copy()
    condition_values = where_condition[pipeline_constants.VALUE]
    if type(condition_values) == list:
        result[VALUE] = condition_values[index]
        return result
    else:
        return result


def __build_mongo_query(joint_type, where_condition):
    if joint_type is None:
        return __process_where_condition(where_condition)
    else:
        where_condition_result = {}
        if joint_type == parameter_constants.AND:
            where_condition_result[mongo_constants.MONGO_AND] = []
            for condition in where_condition:
                where_condition_result[mongo_constants.MONGO_AND].append(__process_where_condition(condition))
        elif joint_type == parameter_constants.OR:
            where_condition_result[mongo_constants.MONGO_OR] = []
            for condition in where_condition:
                where_condition_result[mongo_constants.MONGO_OR].append(__process_where_condition(condition))
        return where_condition_result
