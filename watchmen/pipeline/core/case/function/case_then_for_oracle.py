from typing import List

from watchmen.common.utils.data_utils import build_collection_name
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

from watchmen.pipeline.core.case.model.parameter import Parameter, ParameterJoint
from watchmen.report.model.column import Operator


def parse_parameter(parameter_: Parameter):
    if parameter_.kind == "topic":
        topic = get_topic_by_id(parameter_.topicId)
        topic_name = build_collection_name(topic.name)
        factor = get_factor(parameter_.factorId, topic)
        factor_name = factor.name
        return f'{factor_name.upper()}'
    elif parameter_.kind == 'constant':
        return parameter_.value
    elif parameter_.kind == 'computed':
        if parameter_.type == Operator.add:
            result = None
            for item in parameter_.parameters:
                if result:
                    next_ = parse_parameter(item)
                    result = f'{result}+{next_}'
                else:
                    result = parse_parameter(item)
            return result
        elif parameter_.type == Operator.subtract:
            result = None
            for item in parameter_.parameters:
                if result:
                    next_ = parse_parameter(item)
                    result = f'{result}-{next_}'
                else:
                    result = parse_parameter(item)
            return result
        elif parameter_.type == Operator.multiply:
            result = None
            for item in parameter_.parameters:
                if result:
                    next_ = parse_parameter(item)
                    result = f'{result}*{next_}'
                else:
                    result = parse_parameter(item)
            return result
        elif parameter_.type == Operator.divide:
            result = None
            for item in parameter_.parameters:
                if result:
                    next_ = parse_parameter(item)
                    result = f'{result}/{next_}'
                else:
                    result = parse_parameter(item)
            return result
        elif parameter_.type == Operator.modulus:
            result = None
            for item in parameter_.parameters:
                if result:
                    next_ = parse_parameter(item)
                    result = f'{result}%{next_}'
                else:
                    result = parse_parameter(item)
            return result
        elif parameter_.type == "case-then":
            return parse_oracle_case_then(parameter_.parameters)
        else:
            raise Exception("operator is not supported")


def parse_storage_case_then(parameters_: List[Parameter]) -> any:
    return parse_oracle_case_then(parameters_)


def parse_oracle_case_then(parameters_: List[Parameter]) -> any:
    stmt_when_str = None
    stmt_when = []
    stmt_else = ""
    for param in parameters_:
        if param.on is not None:
            condition = parse_parameter_joint(param.on)
            value = parse_parameter(param)
            stmt = f'WHEN {condition} THEN {value}'
            stmt_when.append(stmt)
        else:
            else_value = parse_parameter(param)
            stmt_else = f'ELSE {else_value} END'
    for item in stmt_when:
        if stmt_when_str is None:
            stmt_when_str = item
        else:
            stmt_when_str = stmt_when_str + " " + item
    return f'CASE {stmt_when_str} {stmt_else}'


def parse_parameter_joint(joint: ParameterJoint):
    results = []
    stmt_where = None
    if joint.jointType is not None:
        if joint.jointType == "and":
            for filter_ in joint.filters:
                results.append(parse_parameter_joint(filter_))
            for item in results:
                if stmt_where is None:
                    stmt_where = item
                else:
                    stmt_where = stmt_where + " and " + item
            return stmt_where
        elif joint.jointType == "or":
            for filter_ in joint.filters:
                results.append(parse_parameter_joint(filter_))
            for item in results:
                if stmt_where is None:
                    stmt_where = item
                else:
                    stmt_where = stmt_where + " or " + item
            return stmt_where
    else:
        left = parse_parameter(joint.left)
        operator_ = joint.operator
        right = parse_parameter(joint.right)
        if operator_ == "equals":
            return f'{left}={right}'
        elif operator_ == "not-equals":
            return f'{left}!={right}'
        elif operator_ == 'empty':
            return f'{left} IS NULL'
        elif operator_ == 'not-empty':
            return f'{left} IS NOT NULL'
        elif operator_ == "more":
            return f'{left}>{right}'
        elif operator_ == "more-equals":
            return f'{left}>={right}'
        elif operator_ == "less":
            return f'{left}<{right}'
        elif operator_ == "less-equals":
            return f'{left}<={right}'
        elif operator_ == 'in':
            return f'{left} in ({right})'
        elif operator_ == 'not-in':
            return f'{left} not in ({right})'
        else:
            raise Exception("operator is not supported")
