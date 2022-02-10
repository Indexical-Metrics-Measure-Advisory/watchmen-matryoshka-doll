
from typing import List

from model.model.report.column import Column
from model.model.report.report import ReportIndicator, ReportDimension
from pypika import functions as fn, AliasedQuery, Field
from watchmen.parser.console_paramter_parser import ConsoleParameterJointParser
from watchmen.parser.parameter import ParameterJoint
from watchmen.report.builder.utils import convent_column_list_to_dict


def build_indicators(indicators: List[ReportIndicator], dataset_columns: List[Column], dataset_query_alias):
    _selects = []
    _appear_in_group_by = []
    columns = convent_column_list_to_dict(dataset_columns)
    for indicator in indicators:
        column: Column = columns.get(indicator.columnId, None)
        if column is None:
            continue
        else:
            field = Field(column.alias, None, AliasedQuery(dataset_query_alias))
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
            field = Field(column.alias, None, AliasedQuery(dataset_query_alias))
            _selects.append(fn.Max(field))  # need put dimension field in select expr, and max mean first in group by
            _groupbys.append(field)
            _orderbys.append(field)
    return _selects, _groupbys, _orderbys


def build_report_where(filter_: ParameterJoint,
                       topic_space_filter,
                       dataset_query_alias,
                       dataset_columns: List[Column]):
    parser_ = ConsoleParameterJointParser(filter_, topic_space_filter, dataset_query_alias, dataset_columns)
    return parser_.parse_parameter_joint()
