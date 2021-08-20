import datetime
import operator
from decimal import Decimal
from typing import List
import arrow

from pypika import Query, Table, JoinType, Order, CustomFunction
from pypika import functions as fn
from pypika.queries import QueryBuilder
from pypika.terms import PseudoColumn, ValueWrapper, LiteralValue

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


def _date_diff(unit, args_str):
    args_list = args_str.split(",")
    if len(args_list) != 2:
        raise ValueError("Date_diff have invalid args", args_list)
    date_diff = CustomFunction("DATE_DIFF", ["col1", "col2", "col3"])
    arg1 = args_list[0].strip()
    arg2 = args_list[1].strip()
    date1 = _process_date_diff_arg(arg1)
    date2 = _process_date_diff_arg(arg2)
    return date_diff(unit, date1, date2)


def _process_date_diff_arg(arg):
    date_fnc = CustomFunction("date", ["col1"])
    if arg == "now":
        date = PseudoColumn('current_date')
    else:
        if "." in arg:
            arg_list = arg.split(".")
            topic_name = arg_list[0].strip()
            factor_name = arg_list[1].strip()
            date = Table("topic_" + topic_name).as_(topic_name)[factor_name]
        else:
            date = date_fnc(arg)
    return date


def parse_parameter(parameter: Parameter, factor=None):
    if parameter.kind == "topic":
        topic = get_topic_by_id(parameter.topicId)
        topic_col_name = build_collection_name(topic.name)
        factor = get_factor(parameter.factorId, topic)
        result = {'type': factor.type, 'value': Table(topic_col_name).as_(topic.name)[factor.name]}
        return result
    elif parameter.kind == 'constant':
        if parameter.value.strip().startswith("{monthDiff"):
            value_ = parameter.value.strip()
            args_str = value_.replace("{monthDiff(", "").replace(")}", "")
            expr = _date_diff("month", args_str)
            result = {"type": "number", "value": expr}
            return result
        elif parameter.value.strip().startswith("{dayDiff"):
            value_ = parameter.value.strip()
            args_str = value_.replace("{dayDiff(", "").replace(")}", "")
            expr = _date_diff("day", args_str)
            result = {"type": "number", "value": expr}
            return result
        else:
            result = {'type': "text", 'value': parameter.value}
            return result
    elif parameter.kind == 'computed':
        result = None
        left = None
        for item in parameter.parameters:
            if left:
                right = parse_parameter(item)
                return _arithmetic_process(parameter.type, left, right)
            else:
                left = parse_parameter(item)
        return result


def _arithmetic_process(operator_, left: dict, right: dict):
    left_type = left.get("type")
    left_value = left.get("value")
    right_type = right.get("type")
    right_value = right.get("value")
    if left_type == right_type:
        if left_type == "text" and right_type == "text":
            if isinstance(left_value, str) and isinstance(right_value, str):
                if left_value.lstrip('-').isdigit() and right_value.lstrip('-').isdigit():
                    left_trans_value = Decimal(left_value)
                    right_trans_value = Decimal(right_value)
                    return {"type": "number", "value": _build_arithmetic_expression(operator_, left_trans_value,
                                                                                    right_trans_value)}
            else:
                return {"type": "number", "value": _build_arithmetic_expression(operator_, left_value,
                                                                                right_value)}
        else:
            return {"type": left_type, "value": _build_arithmetic_expression(operator_, left_value,
                                                                             right_value)}
    else:
        if left_type == "number" and right_type == "text":
            if isinstance(right_value, str):
                if right_value.lstrip('-').isdigit():
                    right_trans_value = Decimal(right_value)
                    return {"type": "number", "value": _build_arithmetic_expression(operator_, left_value,
                                                                                    right_trans_value)}
        else:
            return {"type": left_type, "value": _build_arithmetic_expression(operator_, left_value,
                                                                             right_value)}


def _build_arithmetic_expression(operator_, left_value, right_value):
    if operator_ == Operator.add:
        return (left_value + right_value)
    elif operator_ == Operator.subtract:
        return (left_value - right_value)
    elif operator_ == Operator.multiply:
        return (left_value * right_value)
    elif operator_ == Operator.divide:
        return (left_value / right_value)
    elif operator_ == Operator.modulus:
        return (left_value % right_value)
    else:
        # TODO more operator support
        raise Exception("operator is not supported")


def _select(q: QueryBuilder, column: Column) -> QueryBuilder:
    param = parse_parameter(column.parameter)
    return q.select(param.get("value")).as_(column.alias)


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


def _process_filter_operator(operator_, left: dict, right: dict):
    left_type = left.get("type")
    left_value = left.get("value")
    right_type = right.get("type")
    right_value = right.get("value")
    if left_type == right_type:
        return _build_filter_expression(operator_, left_value, right_value)
    else:
        if left_type == "number" and right_type == "text":
            if operator_ == "in" or operator_ == "not-in":
                if isinstance(right_value, str):
                    right_value_list = right_value.split(",")
                    if left_type == "text":
                        return _build_filter_expression(operator_, left_value, right_value_list)
                    elif left_type == "number":
                        right_value_trans_list = []
                        for value_ in right_value_list:
                            if value_.isdigit():
                                right_value_trans_list.append(Decimal(value_))
                        return _build_filter_expression(operator_, left_value, right_value_trans_list)
            else:
                if isinstance(right_value, str):
                    right_trans_value = Decimal(right_value)
                    return _build_filter_expression(operator_, left_value, right_trans_value)
                else:
                    return _build_filter_expression(operator_, left_value, right_value)
        if left_type == "date" and right_type == "text":
            if isinstance(right_value, str):
                return _build_filter_expression(operator_, left_value, LiteralValue("DATE \'{0}\'".format(arrow.get(right_value).format('YYYY-MM-DD'))))
        elif left_type == "datetime" and right_type == "text":
            return _build_filter_expression(operator_, left_value,
                                            LiteralValue("timestamp \'{0}\'".format(arrow.get(right_value).format('YYYY-MM-DD HH:mm:ss'))))
        else:
            return _build_filter_expression(operator_, left_value, right_value)


def _build_filter_expression(operator_, left_value, right_value):
    if operator_ == "equals":
        return left_value == right_value
    elif operator_ == "not-equals":
        return left_value != right_value
    elif operator_ == 'empty':
        return left_value.isnull()
    elif operator_ == 'not-empty':
        return left_value.notnull()
    elif operator_ == "more":
        return left_value > right_value
    elif operator_ == "more-equals":
        return left_value >= right_value
    elif operator_ == "less":
        return left_value < right_value
    elif operator_ == "less-equals":
        return left_value <= right_value
    elif operator_ == 'in':
        return left_value.isin(right_value)
    elif operator_ == 'not-in':
        return left_value.isin(right_value)
    else:
        # TODO more operator support
        raise Exception("filter operator is not supported")


def _filter_criterion(filter: Filter) -> any:
    left = parse_parameter(filter.left)
    right = parse_parameter(filter.right)
    return _process_filter_operator(filter.operator, left, right)


def _groupby(q: QueryBuilder, column: Column) -> QueryBuilder:
    column_param = parse_parameter(column.parameter)
    return q.groupby(column_param.get("value"))


def _indicator(q: QueryBuilder, indicator: ReportIndicator, column: Column) -> QueryBuilder:
    column_param = parse_parameter(column.parameter)
    value_ = column_param.get("value")
    if indicator.arithmetic == "sum":
        return q.select(fn.Sum(value_))
    elif indicator.arithmetic == "avg":
        return q.select(fn.Avg(value_))
    elif indicator.arithmetic == "max":
        return q.select(fn.Max(value_))
    elif indicator.arithmetic == "min":
        return q.select(fn.Min(value_))
    elif indicator.arithmetic == "count":
        return q.select(fn.Count(value_))
    else:
        return q.select(fn.Max(value_))


def _dimension(q: QueryBuilder, dimension: ReportDimension, column: Column):
    column_param = parse_parameter(column.parameter)
    value_ = column_param.get("value")
    return q.select(fn.Max(value_))


def _orderby(q: QueryBuilder, column: Column, order: str) -> QueryBuilder:
    column_param = parse_parameter(column.parameter)
    value_ = column_param.get("value")
    if order == "asc":
        return q.orderby(value_, order=Order.asc)
    elif order == "desc":
        return q.orderby(value_, order=Order.desc)
    elif order == "none":
        return q.orderby(value_)


def _limit(q: QueryBuilder, count) -> QueryBuilder:
    return q.limit(count)
