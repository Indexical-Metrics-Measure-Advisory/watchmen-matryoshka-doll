import operator
from typing import List

from pypika import Query, Table, Field, JoinType, Criterion
from pypika.queries import QueryBuilder

from watchmen.common.parameter import Parameter, ParameterExpression
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.report.model.column import Column, Operator
from watchmen.report.model.filter import Filter, ConnectiveType
from watchmen.report.model.join import Join, JoinType
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def _from(column: Column) -> QueryBuilder:
    topic = get_topic_by_id(column.parameter.topicId)
    topic_col_name = build_collection_name(topic.name)
    return Query.from_(Table(topic_col_name))


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
        #todo custom function


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
    test = _connective_filter(filter)
    return q.where(test)


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
        return operator.ne(left, right)
    elif filter.operator == "more":
        return operator.gt(left, int(right))
    elif filter.operator == "more-equals":
        return operator.ge(left, int(right))
    elif filter.operator == "less":
        return operator.lt(left, int(right))
    elif filter.operator == "less-equals":
        return operator.le(left, int(right))
    elif filter.operator == "in":
        # TODO
        return left.isin(['a', 'b'])
    else:
        # TODO more operator support
        raise Exception("operator is not supported")

'''
def parse_filter_parameter(parameter: Parameter):
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
                    result = operator.add(result, parse_filter_parameter(item))
                else:
                    result = parse_filter_parameter(item)
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
        #todo custom function
'''