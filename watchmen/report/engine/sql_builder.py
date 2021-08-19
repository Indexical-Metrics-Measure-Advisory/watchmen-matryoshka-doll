import datetime
import operator
from typing import List

from pypika import Query, Table, JoinType, Order, CustomFunction
from pypika import functions as fn
from pypika.queries import QueryBuilder
from pypika.terms import PseudoColumn


from watchmen.common.parameter import Parameter
from watchmen.common.utils.data_utils import build_collection_name
from watchmen.pipeline.utils.units_func import get_factor
from watchmen.report.model.column import Column, Operator
from watchmen.report.model.filter import Filter, ConnectiveType
from watchmen.report.model.join import Join, JoinType
from watchmen.report.model.report import ReportIndicator, ReportDimension
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def _from(column: Column) -> QueryBuilder:
    topic = get_topic_by_id(column.parameter.topicId)
    topic_col_name = build_collection_name(topic.name)
    return Query.from_(Table(topic_col_name).as_(topic.name))


def parse_parameter(parameter: Parameter, factor=None):
    if parameter.kind == "topic":
        topic = get_topic_by_id(parameter.topicId)
        topic_col_name = build_collection_name(topic.name)
        factor = get_factor(parameter.factorId, topic)
        return Table(topic_col_name).as_(topic.name)[factor.name]
    elif parameter.kind == 'constant':
        if parameter.value.strip().startswith("{monthDiff"):
            value_ = parameter.value.strip()
            args_str = value_.replace("{monthDiff(", "").replace(")}", "")
            args_list = args_str.split(",")

            month_diff = CustomFunction("DATE_DIFF", ["col1", "col2", "col3"])
            date_fnc = CustomFunction("date", ["col1"])

            arg1 = args_list[0].strip()
            arg2 = args_list[1].strip()

            if arg1 == "now":
                date1 = PseudoColumn('current_date')
            else:
                if "." in arg1:
                    arg1_list = arg1.split(".")
                    topic_name = arg1_list[0].strip()
                    factor_name = arg1_list[1].strip()
                    date1 = Table("topic_" + topic_name).as_(topic_name)[factor_name]
                else:
                    date1 = date_fnc(arg1)

            if arg2 == "now":
                date2 = PseudoColumn('current_date')
            else:
                if "." in arg2:
                    arg2_list = arg2.split(".")
                    topic_name = arg2_list[0].strip()
                    factor_name = arg2_list[1].strip()
                    date2 = Table("topic_" + topic_name).as_(topic_name)[factor_name]
                else:
                    date2 = date_fnc(arg2)

            return month_diff('month', date1, date2)
        else:
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
            result = None
            for item in parameter.parameters:
                if result:
                    result = operator.sub(result, parse_parameter(item))
                else:
                    result = parse_parameter(item)
            return result
        elif parameter.type == Operator.multiply:
            result = None
            for item in parameter.parameters:
                if result:
                    result = operator.mul(result, (parse_parameter(item)))
                else:
                    result = parse_parameter(item)
            return result
        elif parameter.type == Operator.divide:
            result = None
            left = None
            for item in parameter.parameters:
                if left:
                    right = parse_parameter(item)
                    result = left / right
                else:
                    left = parse_parameter(item)
            return result
        elif parameter.type == Operator.modulus:
            result = None
            for item in parameter.parameters:
                if result:
                    result = operator.mod(result, parse_parameter(item))
                else:
                    result = parse_parameter(item)
            return result
        else:
            # TODO more operator support
            raise Exception("operator is not supported")


def _select(q: QueryBuilder, column: Column) -> QueryBuilder:
    return q.select(parse_parameter(column.parameter)).as_(column.alias)


def _join(q: QueryBuilder, join: Join) -> QueryBuilder:
    # left
    topic = get_topic_by_id(join.topicId)
    topic_col_name = build_collection_name(topic.name)
    factor = get_factor(join.factorId, topic)
    left_table = Table(topic_col_name).as_(topic.name)

    # right
    sec_topic = get_topic_by_id(join.secondaryTopicId)
    sec_topic_col_name = build_collection_name(sec_topic.name)
    sec_factor = get_factor(join.secondaryFactorId, sec_topic)
    right_table = Table(sec_topic_col_name).as_(sec_topic.name)

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
    topic = get_topic_by_id(filter.left.topicId)
    factor = get_factor(filter.left.factorId, topic)
    right = parse_parameter(filter.right, factor)

    if filter.operator == "equals":
        if factor is not None and factor.type == "text":
            return operator.eq(left, right)
        elif factor is not None and factor.type == "date":
            return "{0}=DATE {1}".format(left, right)
        elif factor is not None and factor.type == "datetime":
            return "{0}=TIMESTAMP {1}".format(left, right)
        else:
            return operator.eq(left, right)
    elif filter.operator == "not-equals":
        if factor is not None and factor.type == "text":
            return left.__ne__(right)
        else:
            return left.__ne__(int(right))
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
    elif indicator.arithmetic == "count":
        return q.select(fn.Count(parse_parameter(column.parameter)))
    else:
        return q.select(fn.Max(parse_parameter(column.parameter)))


def _dimension(q: QueryBuilder, dimension: ReportDimension, column: Column):
    return q.select(fn.Max(parse_parameter(column.parameter)))


def _orderby(q: QueryBuilder, column: Column, order: str) -> QueryBuilder:
    if order == "asc":
        return q.orderby(parse_parameter(column.parameter), order=Order.asc)
    elif order == "desc":
        return q.orderby(parse_parameter(column.parameter), order=Order.desc)
    elif order == "none":
        return q.orderby(parse_parameter(column.parameter))


def _limit(q: QueryBuilder, count) -> QueryBuilder:
    return q.limit(count)
