from datetime import datetime
from decimal import Decimal
from typing import List

import arrow

from watchmen.topic.factor.factor import Factor


def cal_factor_value(data_: dict, factor: Factor) -> any:
    if "." in factor.name:
        results = []
        factors = build_factors(factor)
        values = get_factor_value(0, factors, data_, results)
        if len(values) == 1:
            return values[0]
        else:
            return values
    else:
        values = get_value(factor, data_)
    return values


def build_factors(factor: Factor) -> List[Factor]:
    factor_names = factor.name.split(".")
    factors = []
    for name in factor_names:
        factor = Factor()
        factor.name = name
        factors.append(factor)
    return factors


def get_factor_value(index, factors, data_, result):
    factor = factors[index]
    value = get_value(factor, data_)
    if type(value) is list:
        for el in value:
            get_factor_value(index + 1, factors, el, result)
    elif type(value) is dict:
        get_factor_value(index + 1, factors, value, result)
    else:
        if value is None and factor.defaultValue is not None:
            result.append(convert_value_type_by_factor_type(factor.defaultValue, factor.type))
        else:
            result.append(value)

    return result


def get_value(factor: Factor, data):
    if factor.name in data:
        value = data[factor.name]
        if value is None:
            return value
        else:
            return convert_value_type_by_factor_type(value, factor.type)
    else:
        return None


def convert_value_type_by_factor_type(value: any, type_: str) -> any:
    if value is None:
        return None
    elif type_ == "text":
        return str(value)
    elif type_ == "number":
        return Decimal(value)
    elif type_ == "datetime":
        return convert_datetime(value)
    elif type_ == "boolean":
        return bool(value)
    elif type_ == "sequence":
        return int(value)
    elif type_ == "year":
        return int(value)
    elif type_ == "month":
        return int(value)
    elif type_ == "time":
        return arrow.get(value).datetime.replace(tzinfo=None)
    elif type_ == "date":
        return convert_date(value)
    else:
        return value


def convert_date(value):
    if value is not None:
        if isinstance(value, datetime):
            return arrow.get(value).date()
        else:
            return arrow.get(value).date()
    else:
        return value


def convert_datetime(value):
    if value is not None:
        if isinstance(value, datetime):
            return value.replace(tzinfo=None)
        else:
            return arrow.get(value).datetime.replace(tzinfo=None)
    else:
        return value
