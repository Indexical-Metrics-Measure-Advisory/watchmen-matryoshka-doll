import operator
from decimal import Decimal
from typing import List
from model.model.report.column import Operator

from watchmen_boot.guid.snowflake import get_surrogate_key
from watchmen_boot.utils.date_func import parsing_and_formatting, YEAR, MONTH, WEEK_OF_YEAR, DAY_OF_WEEK, WEEK_OF_MONTH, \
    QUARTER, HALF_YEAR, DAY_OF_MONTH

from watchmen.common.utils.data_utils import build_collection_name
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
from watchmen.pipeline.utils.units_func import get_factor
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
                        if real_name == "nextSeq":
                            res = get_surrogate_key()
                        else:
                            res = instance.get(real_name)
                    elif var_name == "snowflake":  # use nextSeq, prepare to remove in next version todo
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
            left = None
            for item in parameter_.parameters:
                if left is not None:
                    right = parse_parameter(item, instance, variables)
                    if right is None:
                        right = 0
                    elif isinstance(right, str):
                        if right.lstrip('-').isdigit():
                            right = Decimal(right)
                    result = operator.add(left, right)
                else:
                    left = parse_parameter(item, instance, variables)
                    if left is None:
                        left = 0
                    elif isinstance(left, str):
                        if left.lstrip('-').isdigit():
                            left = Decimal(left)
            return result
        elif parameter_.type == Operator.subtract:
            result = None
            left = None
            for item in parameter_.parameters:
                if left is not None:
                    right = parse_parameter(item, instance, variables)
                    if right is None:
                        right = 0
                    elif isinstance(right, str):
                        if right.lstrip('-').isdigit():
                            right = Decimal(right)
                    result = operator.sub(left, right)
                else:
                    left = parse_parameter(item, instance, variables)
                    if left is None:
                        left = 0
                    elif isinstance(left, str):
                        if left.lstrip('-').isdigit():
                            left = Decimal(left)
            return result
        elif parameter_.type == Operator.multiply:
            result = None
            left = None
            for item in parameter_.parameters:
                if left is not None:
                    right = parse_parameter(item, instance, variables)
                    if right is None:
                        right = 0
                    elif isinstance(right, str):
                        if right.lstrip('-').isdigit():
                            right = Decimal(right)
                    result = operator.mul(left, right)
                else:
                    left = parse_parameter(item, instance, variables)
                    if left is None:
                        left = 0
                    elif isinstance(left, str):
                        if left.lstrip('-').isdigit():
                            left = Decimal(left)
            return result
        elif parameter_.type == Operator.divide:
            result = None
            left = None
            for item in parameter_.parameters:
                if left is not None:
                    right = parse_parameter(item, instance, variables)
                    if right is None:
                        right = 0
                    elif isinstance(right, str):
                        if right.lstrip('-').isdigit():
                            right = Decimal(right)
                    result = operator.truediv(left, right)
                else:
                    left = parse_parameter(item, instance, variables)
                    if left is None:
                        left = 0
                    elif isinstance(left, str):
                        if left.lstrip('-').isdigit():
                            left = Decimal(left)
            return result
        elif parameter_.type == Operator.modulus:
            result = None
            left = None
            for item in parameter_.parameters:
                if left is not None:
                    right = parse_parameter(item, instance, variables)
                    if right is None:
                        right = 0
                    elif isinstance(right, str):
                        if right.lstrip('-').isdigit():
                            right = Decimal(right)
                    result = operator.mod(left, right)
                else:
                    left = parse_parameter(item, instance, variables)
                    if left is None:
                        left = 0
                    elif isinstance(left, str):
                        if left.lstrip('-').isdigit():
                            left = Decimal(left)
            return result
        elif parameter_.type == "year-of":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            if result is not None:
                return parsing_and_formatting(convert_datetime(result), YEAR)
            else:
                return result
        elif parameter_.type == "month-of":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            if result is not None:
                return parsing_and_formatting(convert_datetime(result), MONTH)
            else:
                return result
        elif parameter_.type == "week-of-year":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            return parsing_and_formatting(convert_datetime(result), WEEK_OF_YEAR)
        elif parameter_.type == "day-of-week":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            return parsing_and_formatting(convert_datetime(result), DAY_OF_WEEK)
        elif parameter_.type == "week-of-month":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            return parsing_and_formatting(convert_datetime(result), WEEK_OF_MONTH)
        elif parameter_.type == "quarter-of":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            return parsing_and_formatting(convert_datetime(result), QUARTER)
        elif parameter_.type == "half-year-of":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            return parsing_and_formatting(convert_datetime(result), HALF_YEAR)
        elif parameter_.type == "day-of-month":
            result = parse_parameter(parameter_.parameters[0], instance, variables)
            return parsing_and_formatting(convert_datetime(result), DAY_OF_MONTH)
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
    if default_ is not None:
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
            return do_equals_with_value_type_check(left, right)
        elif operator_ == "not-equals":
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
            return do_more_with_value_type_check(left, right)
        elif operator_ == "more-equals":
            return do_more_equals_with_value_type_check(left, right)
        elif operator_ == "less":
            return do_less_with_value_type_check(left, right)
        elif operator_ == "less-equals":
            return do_less_equals_with_value_type_check(left, right)
        elif operator_ == 'in':
            return do_in_with_value_type_check(left, right)
        elif operator_ == 'not-in':
            return do_not_in_with_value_type_check(left, right)
        else:
            raise Exception("operator is not supported")
