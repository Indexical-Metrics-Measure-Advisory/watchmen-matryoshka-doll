from typing import List

import arrow
from pypika import functions as fn, AliasedQuery, Field, Criterion
from pypika.terms import LiteralValue
from watchmen.report.model.consume_model import Indicator


def build_indicators(indicators: List[Indicator], dataset_query_alias):
    _selects = []
    _appear_in_group_by = []
    table = AliasedQuery(dataset_query_alias)
    for indicator in indicators:
        field = Field(indicator.name, None, table)
        if indicator.arithmetic == "sum":
            _selects.append(fn.Sum(field, indicator.alias))
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


def build_where(where_, dataset_query_alias):
    if where_.jointType:
        if where_.jointType == "and":
            return Criterion.all([build_where(item, dataset_query_alias) for item in where_.filters])
        elif where_.jointType == "or":
            return Criterion.any([build_where(item, dataset_query_alias) for item in where_.filters])
    else:
        return build_criterion(where_, dataset_query_alias)


def build_criterion(where_, dataset_query_alias):
    table = AliasedQuery(dataset_query_alias)
    field = Field(where_.name, None, table)
    type_ = where_.type
    operator_ = where_.operator
    value = where_.value
    if type_ == "date":
        if isinstance(value, list):
            value_ = []
            for v in value:
                value_.append(LiteralValue("DATE \'{0}\'".format(arrow.get(v).format('YYYY-MM-DD'))))
        else:
            value_ = LiteralValue("DATE \'{0}\'".format(arrow.get(value).format('YYYY-MM-DD')))
    elif type_ == "datetime":
        if isinstance(value, list):
            value_ = []
            for v in value:
                value_.append(LiteralValue("timestamp \'{0}\'".format(arrow.get(v).format('YYYY-MM-DD HH:mm:ss'))))
        else:
            value_ = LiteralValue("timestamp \'{0}\'".format(arrow.get(value).format('YYYY-MM-DD HH:mm:ss')))
    else:
        value_ = value
    return _build_criterion_expression(operator_, field, value_)


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
    elif operator_ == "between":
        if isinstance(right, list):
            return left.between(right[0], right[1])
        else:
            raise ValueError("the value {0} should be list in between operator".format(right))
    else:
        # TODO more operator support
        raise NotImplementedError("filter operator is not supported")
