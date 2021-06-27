from decimal import Decimal

import operator
from typing import List

import pandas as pd

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.pipeline.core.by.parse_on_parameter import __week_number_of_month
from watchmen.pipeline.core.case.function.utils import parse_constant_expression, AMP, FUNC, \
    get_variable_with_func_pattern, DOT, get_variable_with_dot_pattern
from watchmen.pipeline.core.case.model.parameter import Parameter, ParameterJoint
from watchmen.pipeline.core.parameter.operator.equals import do_equals_with_value_type_check
from watchmen.pipeline.core.parameter.operator.in_operator import do_in_with_value_type_check
from watchmen.pipeline.core.parameter.operator.less import do_less_with_value_type_check
from watchmen.pipeline.core.parameter.operator.less_equals import do_less_equals_with_value_type_check
from watchmen.pipeline.core.parameter.operator.more import do_more_with_value_type_check
from watchmen.pipeline.core.parameter.operator.more_equals import do_more_equals_with_value_type_check
from watchmen.pipeline.core.parameter.operator.not_equals import do_not_equals_with_value_type_check
from watchmen.pipeline.core.parameter.operator.not_in_operator import do_not_in_with_value_type_check
from watchmen.pipeline.core.parameter.utils import cal_factor_value, convert_datetime, check_and_convert_value_by_factor
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.report.model.column import Operator
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def parse_parameter(parameter_: Parameter, instance, variables):
    if parameter_.kind == "topic":
        topic = get_topic_by_id(parameter_.topicId)
        topic_name = build_collection_name(topic.name)
        factor = get_factor(parameter_.factorId, topic)
        value_ = cal_factor_value(instance, factor)
        return check_and_convert_value_by_factor(factor, value_)
    elif parameter_.kind == 'constant':
        if parameter_.value is None:
            return None
        elif parameter_.value == '':
            return ''
        elif not parameter_.value:
            return None
        else:
            it = parse_constant_expression(parameter_.value)
            for item in it:
                if item.startswith('{') and item.endswith('}'):
                    var_name = item.lstrip('{').rstrip('}')
                    res = None
                    if var_name.startswith(AMP):
                        real_name = var_name.lstrip('&')
                        res = instance.get(real_name)
                    elif var_name == "snowflake":
                        res = get_surrogate_key()
                    elif FUNC in var_name:
                        res = get_variable_with_func_pattern(var_name, variables)
                    elif DOT in var_name:
                        res = get_variable_with_dot_pattern(var_name, variables)
                    else:
                        if var_name in variables:
                            res = variables[var_name]
                    return res
            return parameter_.value
    elif parameter_.kind == 'computed':
        if parameter_.type == Operator.add:
            result = None
            for item in parameter_.parameters:
                if result:
                    result = operator.add(result, parse_parameter(item, instance, variables))
                else:
                    result = parse_parameter(item, instance, variables)
            return result
        elif parameter_.type == Operator.subtract:
            result = None
            for item in parameter_.parameters:
                if result:
                    result = operator.sub(result, parse_parameter(item, instance, variables))
                else:
                    result = parse_parameter(item, instance, variables)
            return result
        elif parameter_.type == Operator.multiply:
            result = None
            for item in parameter_.parameters:
                if result:
                    result = operator.mul(result, parse_parameter(item, instance, variables))
                else:
                    result = parse_parameter(item, instance, variables)
            return result
        elif parameter_.type == Operator.divide:
            result = None
            for item in parameter_.parameters:
                if result:
                    result = operator.truediv(result, parse_parameter(item, instance, variables))
                else:
                    result = parse_parameter(item, instance, variables)
            return result
        elif parameter_.type == Operator.modulus:
            result = None
            for item in parameter_.parameters:
                if result:
                    result = operator.mod(result, parse_parameter(item, instance, variables))
                else:
                    result = parse_parameter(item, instance, variables)
            return result
        elif parameter_.type == "year-of":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            if result is not None:
                return convert_datetime(result).year
            else:
                result
        elif parameter_.type == "month-of":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            if result is not None:
                return convert_datetime(result).month
            else:
                result
        elif parameter_.type == "week-of-year":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            return convert_datetime(result).isocalendar()[1]
        elif parameter_.type == "day-of-week":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            return convert_datetime(result).weekday()
        elif parameter_.type == "day-of-month":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            return __week_number_of_month(convert_datetime(result).date())
        elif parameter_.type == "quarter-of":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            quarter = pd.Timestamp(convert_datetime(result)).quarter
            return quarter
        elif parameter_.type == "half-year-of":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            month = convert_datetime(result).month
            if month <= 6:
                return 1
            else:
                return 2
        elif parameter_.type == "day-of-month":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            return convert_datetime(result).day
        elif parameter_.type == "case-then":
            return parse_mapper_case_then(parameter_.parameters, instance, variables)
        else:
            raise Exception("operator is not supported")


def parse_mapper_case_then(parameters: List[Parameter], instance, variables) -> any:
    default_ = None
    for param in parameters:
        if param.on:
            condition = parse_parameter_joint(param.on, instance, variables)
            if condition:
                return parse_parameter(param, instance, variables)
        else:
            default_ = parse_parameter(param, instance, variables)
    if default_:
        return default_
    else:
        return None


def parse_parameter_joint(joint: ParameterJoint, instance, variables):
    results = []
    if joint.jointType is not None:
        if joint.jointType == "and":
            for filter_ in joint.filters:
                results.append(parse_parameter_joint(filter_, instance, variables))
            if False in results:
                return False
            else:
                return True
        elif joint.jointType == "or":
            for filter_ in joint.filters:
                results.append(parse_parameter_joint(filter_, instance, variables))
            if True in results:
                return True
            else:
                return False
    else:
        left = parse_parameter(joint.left, instance, variables)
        operator_ = joint.operator
        right = parse_parameter(joint.right, instance, variables)
        if operator_ == "equals":
            # return operator.eq(left, right)
            return do_equals_with_value_type_check(left, right)
        elif operator_ == "not-equals":
            # return operator.ne(left, right)
            return do_not_equals_with_value_type_check(left, right)
        elif operator_ == 'empty':
            if left == "":
                return operator.is_(None, None)
            return operator.is_(left, None)
        elif operator_ == 'not-empty':
            if left == "":
                return operator.is_not(None, None)
            return operator.is_not(left, None)
        elif operator_ == "more":
            # return operator.gt(left, right)
            return do_more_with_value_type_check(left, right)
        elif operator_ == "more-equals":
            # return operator.ge(left, right)
            return do_more_equals_with_value_type_check(left,right)
        elif operator_ == "less":
            # return operator.lt(left, right)
            return do_less_with_value_type_check(left, right)
        elif operator_ == "less-equals":
            # return operator.le(left, right)
            return do_less_equals_with_value_type_check(left, right)
        elif operator_ == 'in':
            return do_in_with_value_type_check(left, right)
        elif operator_ == 'not-in':
            return do_not_in_with_value_type_check(left, right)
        else:
            raise Exception("operator is not supported")
