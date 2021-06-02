from __future__ import annotations

from typing import List

import operator

from storage.utils.storage_utils import build_collection_name
from watchmen.pipeline.core.case.function.utils import parse_constant_expression, AMP, FUNC, \
    get_variable_with_func_pattern, DOT, get_variable_with_dot_pattern
from watchmen.pipeline.core.case.model.parameter import Parameter, ParameterJoint
from watchmen.pipeline.core.parameter.utils import cal_factor_value
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.report.model.column import Operator
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def parse_parameter(parameter_: Parameter, instance, variables):
    if parameter_.kind == "topic":
        topic = get_topic_by_id(parameter_.topicId)
        topic_name = build_collection_name(topic.name)
        factor = get_factor(parameter_.factorId, topic)
        return cal_factor_value(instance, factor)
    elif parameter_.kind == 'constant':
        if parameter_.value is None:
            return None
        elif parameter_.value == '':
            return ''
        elif not parameter_.value:
            return None
        else:
            result = []
            it = parse_constant_expression(parameter_.value)
            for item in it:
                if item.startswith('{') and item.endswith('}'):
                    var_name = item.lstrip('{').right('}')
                    if var_name.startswith(AMP):
                        real_name = var_name.lstrip('&')
                        res = instance.get(real_name)
                        result.append(res)
                    elif FUNC in var_name:
                        res = get_variable_with_func_pattern(var_name, variables)
                        result.append(res)
                    elif DOT in var_name:
                        res = get_variable_with_dot_pattern(var_name, variables)
                        result.append(res)
                else:
                    result.append(item)

            return ''.join(result)
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
        elif parameter_.type == "case-then":
            return parse_mapper_case_then(parameter_.parameters, instance, variables)
        else:
            raise Exception("operator is not supported")


def parse_mapper_case_then(parameters: List[Parameter], instance, variables) -> any:
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
            return operator.eq(left, right)
        elif operator_ == "not-equals":
            return operator.ne(left, right)
        elif operator_ == 'empty':
            return left.isnull()
        elif operator_ == 'not-empty':
            return left.notnull()
        elif operator_ == "more":
            return operator.gt(left, right)
        elif operator_ == "more-equals":
            return operator.ge(left, right)
        elif operator_ == "less":
            return operator.lt(left, right)
        elif operator_ == "less-equals":
            return operator.le(left, right)
        elif operator_ == 'in':
            value_list = right.split(',')
            values: List = []
            for value in value_list:
                if value.isdigit():
                    values.append(int(value))
                else:
                    values.append(value)
            return left.isin(values)
        elif operator_ == 'not-in':
            value_list = right.split(',')
            values: List = []
            for value in value_list:
                if value.isdigit():
                    values.append(int(value))
                else:
                    values.append(value)
            return left.notin(values)
        else:
            raise Exception("operator is not supported")
