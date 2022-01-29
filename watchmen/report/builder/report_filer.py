from decimal import Decimal
from typing import List

from watchmen.common.presto import presto_fn

from arrow import arrow
from model.model.common.parameter import Parameter, ParameterJoint
from model.model.report.column import Column
from model.model.report.report import ReportIndicator, ReportDimension
from pypika import functions as fn, AliasedQuery, Field
from pypika.terms import LiteralValue, Criterion, Term

from watchmen.pipeline.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def build_indicators(indicators: List[ReportIndicator], dataset_columns: List[Column], dataset_query_alias):
    _selects = []
    _appear_in_group_by = []
    columns = convent_column_list_to_dict(dataset_columns)
    for indicator in indicators:
        column: Column = columns.get(indicator.columnId, None)
        if column is None:
            continue
        else:
            # should use alias?
            # field = Field(column.alias, None, AliasedQuery(dataset_query_alias))
            field = parse_column_parameter(column, dataset_query_alias)["value"]
            if indicator.arithmetic == "sum":
                _selects.append(fn.Sum(field))
            elif indicator.arithmetic == "avg":
                _selects.append(fn.Avg(field))
            elif indicator.arithmetic == "max":
                _selects.append(fn.Max(field))
            elif indicator.arithmetic == "min":
                _selects.append(fn.Min(field))
            elif indicator.arithmetic == "count":
                _selects.append(fn.Count(field))
            else:
                _selects.append(field)
                _appear_in_group_by.append(field)
    return _selects, _appear_in_group_by


def build_dimensions(dimensions: List[ReportDimension], dataset_columns: List[Column], dataset_query_alias):
    _selects = []
    _groupbys = []
    _orderbys = []
    columns = convent_column_list_to_dict(dataset_columns)
    for dimension in dimensions:
        column: Column = columns.get(dimension.columnId, None)
        if column is None:
            continue
        else:
            # field = Field(column.alias, None, AliasedQuery(dataset_query_alias))
            field = parse_column_parameter(column, dataset_query_alias)["value"]
            _selects.append(fn.Max(field))  # need put dimension field in select expr, and max mean first in group by
            _groupbys.append(field)
            _orderbys.append(field)
    return _selects, _groupbys, _orderbys


def build_report_where(filter: ParameterJoint, dataset_columns: List[Column], dataset_query_alias):
    if filter.jointType:
        if filter.jointType == "and":
            return Criterion.all(
                [build_report_where(item, dataset_columns, dataset_query_alias) for item in filter.filters])
        elif filter.jointType == "or":
            return Criterion.any(
                [build_report_where(item, dataset_columns, dataset_query_alias) for item in filter.filters])
    else:
        return build_criterion(filter, dataset_columns, dataset_query_alias)


def build_criterion(filter, dataset_columns: List[Column], dataset_query_alias) -> Criterion:
    operator_ = filter.operator
    left = parse_report_filter_parameter(filter.left, dataset_columns, dataset_query_alias)
    right = parse_report_filter_parameter(filter.right, dataset_columns, dataset_query_alias)

    lvalue = left["value"]
    ltype = left["type"]

    rvalue = right["value"]
    rtype = right["type"]

    if operator_ == "empty" or operator_ == "not-empty":
        return _build_criterion_expression(operator_, lvalue, rvalue)
    if ltype == rtype:
        return _build_criterion_expression(operator_, lvalue, rvalue)
    else:
        if ltype == "number" and rtype == "text":
            if operator_ == "in" or operator_ == "not-in":
                if isinstance(rvalue, str):
                    right_value_list = rvalue.split(",")
                    right_value_trans_list = []
                    for value_ in right_value_list:
                        if value_.isdigit():
                            right_value_trans_list.append(Decimal(value_))
                    return _build_criterion_expression(operator_, lvalue, right_value_trans_list)
            else:
                if isinstance(rvalue, str):
                    right_trans_value = Decimal(rvalue)
                    return _build_criterion_expression(operator_, lvalue, right_trans_value)
                else:
                    return _build_criterion_expression(operator_, lvalue, rvalue)
        if ltype == "date" and rtype == "text":
            if isinstance(rvalue, str):
                return _build_criterion_expression(operator_, lvalue, LiteralValue(
                    "DATE \'{0}\'".format(arrow.get(rvalue).format('YYYY-MM-DD'))))
        elif ltype == "datetime" and rtype == "text":
            return _build_criterion_expression(operator_, lvalue,
                                               LiteralValue("timestamp \'{0}\'".format(
                                                   arrow.get(rvalue).format('YYYY-MM-DD HH:mm:ss'))))
        else:
            return _build_criterion_expression(operator_, lvalue, rvalue)


def _build_criterion_expression(operator_, left, right):
    if operator_ == "equals":
        return left.eq(right)
    elif operator_ == "not-equals":
        return left.ne(right)
    elif operator_ == 'empty':
        return left.isnull()
    elif operator_ == 'not-empty':
        return left.notnull()
    elif operator_ == "more":
        return left.gt(right)
    elif operator_ == "more-equals":
        return left.gte(right)
    elif operator_ == "less":
        return left.lt(right)
    elif operator_ == "less-equals":
        return left.lte(right)
    elif operator_ == 'in':
        return left.isin(right)
    elif operator_ == 'not-in':
        return left.notin(right)
    else:
        # TODO more operator support
        raise NotImplementedError("filter operator is not supported")


def convent_column_list_to_dict(columns) -> dict:
    columns_dict = {}
    for column in columns:
        columns_dict[column.columnId] = column
    return columns_dict


def parse_report_filter_parameter(parameter: Parameter, dataset_columns, dataset_query_alias):
    if parameter.kind == "topic":
        for column in dataset_columns:
            if column.columnId == parameter.factorId:
                return parse_column_parameter(column, dataset_query_alias)
    elif parameter.kind == 'constant':
        return {"value": Term.wrap_constant(parameter.value), "type": "text"}


def parse_column_parameter(column, dataset_query_alias):
    parameter = column.parameter
    # print(parameter)
    if parameter.kind == "topic":
        topic = get_topic_by_id(parameter.topicId)
        table = AliasedQuery(dataset_query_alias)
        factor = get_factor(parameter.factorId, topic)
        field = Field(column.alias, None, table)
        return {"value": field, "type": factor.type}
    elif parameter.kind == "computed":
        if parameter.type == "month-of":
            result = parameter.parameters[0]
            factor, table = build_chart_indicator_field(dataset_query_alias, result)
            field = presto_fn.PrestoMonth(Field(factor.name, table=table))
            return {"value": field, "type": factor.type}
        elif parameter.type == "year-of":
            result = parameter.parameters[0]
            factor, table =  build_chart_indicator_field(dataset_query_alias, result)
            field = presto_fn.PrestoYear(Field(factor.name, table=table))
            return {"value": field, "type": factor.type}


def build_chart_indicator_field(dataset_query_alias, result):
    topic = get_topic_by_id(result.topicId)
    table = AliasedQuery(dataset_query_alias)
    factor = get_factor(result.factorId, topic)

    return factor,table
