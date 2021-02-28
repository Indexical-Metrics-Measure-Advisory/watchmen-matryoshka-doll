import operator
from typing import List

from pypika import Query, Table, JoinType
from pypika import functions as fn
from pypika.queries import QueryBuilder

from watchmen.common.parameter import Parameter
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.report.model.column import Column, Operator
from watchmen.report.model.filter import Filter, ConnectiveType
from watchmen.report.model.join import Join, JoinType
from watchmen.report.model.report import ReportIndicator, ReportDimension
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def _from(column: Column) -> QueryBuilder:
    topic = get_topic_by_id(column.parameter.topicId)
    topic_col_name = build_collection_name(topic.name)
    return Query.from_(Table(topic_col_name))


def parse_parameter(parameter: Parameter):
    if parameter.kind == "topic":
        topic = get_topic_by_id(parameter.topicId)
        topic_col_name = build_collection_name(topic.name)
        factor = get_factor(parameter.factorId, topic)
        return Table(topic_col_name)[factor.name]
    elif parameter.kind == 'constant':
        return parameter.value
    elif parameter.kind == 'computed':
        if parameter.type == Operator.add:
            result = None
            for item in parameter.parameters:
                if result:
                    result = operator.add(result, parse_parameter(item))
                else:
                    result = parse_parameter(item)
            return result
        elif parameter.type == Operator.subtract:
            pass
        elif parameter.type == Operator.subtract:
            pass
        elif parameter.type == Operator.multiply:
            pass
        elif parameter.type == Operator.divide:
            pass
        elif parameter.type == Operator.modulus:
            pass
        # todo custom function


'''
def parse_parameter(parameter: Parameter):
    if isinstance(parameter, dict):
        return parse_dict_parameter(parameter)
    if isinstance(parameter, Parameter):
        return parse_object_parameter(parameter)


def parse_object_parameter(parameter: Parameter):
    if parameter.kind == "topic":
        topic = get_topic_by_id(parameter.topicId)
        topic_col_name = build_collection_name(topic.name)
        factor = get_factor(parameter.factorId, topic)
        return Table(topic_col_name)[factor.name]
    elif parameter.kind == 'constant':
        return parameter.value
    elif parameter.kind == 'computed':
        if parameter.type == Operator.add:
            result = None
            for item in parameter.parameters:
                if result:
                    result = operator.add(result, parse_parameter(item))
                else:
                    result = parse_parameter(item)
            return result
        elif parameter.type == Operator.subtract:
            pass
        elif parameter.type == Operator.subtract:
            pass
        elif parameter.type == Operator.multiply:
            pass
        elif parameter.type == Operator.divide:
            pass
        elif parameter.type == Operator.modulus:
            pass
        # todo custom function


def parse_dict_parameter(parameter: dict):
    if parameter.get('kind') == "topic":
        topic = get_topic_by_id(parameter.get('topicId'))
        topic_col_name = build_collection_name(topic.name)
        factor = get_factor(parameter.get('factorId'), topic)
        return Table(topic_col_name)[factor.name]
    elif parameter.get('kind') == 'constant':
        return parameter.get('value')
    elif parameter.get('kind') == 'computed':
        if parameter.get('type') == Operator.add:
            result = None
            for item in parameter.get('parameters', []):
                if result:
                    result = operator.add(result, parse_parameter(item))
                else:
                    result = parse_parameter(item)
            return result
        elif parameter.get('type') == Operator.subtract:
            pass
        elif parameter.get('type') == Operator.subtract:
            pass
        elif parameter.get('type') == Operator.multiply:
            pass
        elif parameter.get('type') == Operator.divide:
            pass
        elif parameter.get('type') == Operator.modulus:
            pass
        # todo custom function
'''


def _select(q: QueryBuilder, column: Column) -> QueryBuilder:
    return q.select(parse_parameter(column.parameter)).as_(column.alias)


def _join(q: QueryBuilder, join: Join) -> QueryBuilder:
    # left
    topic = get_topic_by_id(join.topicId)
    topic_col_name = build_collection_name(topic.name)
    factor = get_factor(join.factorId, topic)
    left_table = Table(topic_col_name)

    # right
    sec_topic = get_topic_by_id(join.secondaryTopicId)
    sec_topic_col_name = build_collection_name(sec_topic.name)
    sec_factor = get_factor(join.secondaryFactorId, sec_topic)
    right_table = Table(sec_topic_col_name)

    if join.type == JoinType.inner:
        return q.join(right_table, JoinType.inner).on(
            operator.eq(left_table[factor.name], right_table[sec_factor.name]))

    if join.type == JoinType.left:
        return q.join(right_table, JoinType.left).on(
            operator.eq(left_table[factor.name], right_table[sec_factor.name]))

    if join.type == JoinType.right:
        return q.join(right_table, JoinType.right).on(
            operator.eq(left_table[factor.name], right_table[sec_factor.name]))


def _filter(q: QueryBuilder, filter: Filter) -> QueryBuilder:
    if len(filter.filters) > 0:
        where = _connective_filter(filter)
        return q.where(where)
    else:
        return q


def _connective_filter(filter: Filter):
    result = None
    criterion_list: List = []
    for item in filter.filters:
        if item.__class__.__name__ == 'ParameterExpression':
            criterion_list.append(_filter_criterion(item))
            continue
        if item.jointType:
            criterion_list.append(_connective_filter(item))
        else:
            criterion_list.append(_filter_criterion(item))

    if filter.jointType == ConnectiveType.and_type:
        for criterion in criterion_list:
            if result is not None:
                result = (result) & (criterion)
            else:
                result = criterion

    if filter.jointType == ConnectiveType.or_type:
        for criterion in criterion_list:
            if result is not None:
                result = (result) | (criterion)
            else:
                result = criterion

    return result


def _filter_criterion(filter: Filter) -> any:
    left = parse_parameter(filter.left)
    right = parse_parameter(filter.right)
    if filter.operator == "equals":
        if right.isdigit():
            return operator.eq(left, int(right))
        else:
            return operator.eq(left, right)
    elif filter.operator == "not-equals":
        if right.isdigit():
            return left.__ne__(int(right))
        else:
            return left.__ne__(right)
    elif filter.operator == 'empty':
        return left.isnull()
    elif filter.operator == 'not-empty':
        return left.notnull()
    elif filter.operator == "more":
        return operator.gt(left, int(right))
    elif filter.operator == "more-equals":
        return operator.ge(left, int(right))
    elif filter.operator == "less":
        return operator.lt(left, int(right))
    elif filter.operator == "less-equals":
        return operator.le(left, int(right))
    elif filter.operator == 'in':
        value_list = right.split(',')
        values: List = []
        for value in value_list:
            if value.isdigit():
                values.append(int(value))
            else:
                values.append(value)
        return left.isin(values)
    elif filter.operator == 'not-in':
        value_list = right.split(',')
        values: List = []
        for value in value_list:
            if value.isdigit():
                values.append(int(value))
            else:
                values.append(value)
        return left.notin(values)
    else:
        # TODO more operator support
        raise Exception("operator is not supported")


def _groupby(q: QueryBuilder, column: Column) -> QueryBuilder:
    return q.groupby(parse_parameter(column.parameter))


def _indicator(q: QueryBuilder, indicator: ReportIndicator, column: Column) -> QueryBuilder:
    if indicator.arithmetic == "sum":
        return q.select(fn.Sum(parse_parameter(column.parameter)))
    elif indicator.arithmetic == "avg":
        return q.select(fn.Avg(parse_parameter(column.parameter)))
    elif indicator.arithmetic == "max":
        return q.select(fn.Max(parse_parameter(column.parameter)))
    elif indicator.arithmetic == "min":
        return q.select(fn.Min(parse_parameter(column.parameter)))
    else:
        return q.select(fn.Max(parse_parameter(column.parameter)))


def _dimension(q: QueryBuilder, dimension: ReportDimension, column: Column):
    return q.select(fn.Max(parse_parameter(column.parameter)))


def _orderby(q: QueryBuilder, column: Column) -> QueryBuilder:
    return q.orderby(parse_parameter(column.parameter))
