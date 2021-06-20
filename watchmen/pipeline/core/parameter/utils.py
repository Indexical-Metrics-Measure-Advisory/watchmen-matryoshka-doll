from datetime import datetime
from decimal import Decimal
from typing import List

import arrow

from watchmen.topic.factor.factor import Factor

'''
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
'''
'''
def build_factors(factor: Factor) -> List[Factor]:
    factor_names = factor.name.split(".")
    factors = []
    for name in factor_names:
        factor = Factor()
        factor.name = name
        factors.append(factor)
    return factors
'''

'''
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
'''

'''
def get_value(factor: Factor, data):
    if factor.name in data:
        value = data[factor.name]
        if value is None:
            return value
        else:
            return convert_value_type_by_factor_type(value, factor.type)
    else:
        return None
'''


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


def cal_factor_value(data_, factor):
    """Get factor value from raw_data by the factor name
    raw data have tree and record tow structures

    E.g.::
        tree structure
            {"a":[{"b":[{"c":[{"d":1},{"d":2}]}]},{"b":[{"c":[{"d":3},{"d":4}]}]}]}
            {"a":1,"b":2,"c":{"c1":[{"c11":1,"c12":2,"c13":3},{"c11":4,"c12":5,"c13":6}]}}
        record structure
            {"a":1,"b":2,"c":3}

    According to factor name，get the node structure information, like: a, a.b, a.b.c, a.b.c.d
    the value which get from data should be array, object or basic type

    In the tree structure, the set of data needs to be gradually reduced, so need use
    get_factor_value return for the next loop input parameter

    if not get value, return None
    """
    prefix = None
    result = {}
    data = data_
    for name in factor.name.split("."):
        data, prefix = get_factor_value(data, name, prefix, result)
    if type(result[factor.name]) is list:
        if len(result[factor.name]) == 1:
            return result[factor.name][0]
        elif len(result[factor.name]) == 0:
            return None
        else:
            return result[factor.name]
    else:
        return result[factor.name]


def get_factor_value(data, name, prefix, result):
    """Get value from data by name
    then by "prefix+name" as key, put the value in result
    return result[key] and new prefix

    When the data is list, need loop the data.
    In this case, the default value of result[key] is empty array,
    if value is list, extend value in the result[key] or append value

    if not get value, set result[key] as None or []
    """
    if prefix is None:
        key = name
    else:
        key = prefix + name
    if data is None:
        result[key] = None
    elif type(data) is list:
        result[key] = []
        for item in data:
            value = item.get(name, None)
            if value is not None:
                if type(value) is list:
                    result[key].extend(value)
                else:
                    result[key].append(value)
    else:
        result[key] = data.get(name, None)
    prefix = key + "."
    return result[key], prefix


'''
def check_and_convert_value_by_factor(factor: Factor, value):
    try:
        if factor.type == TEXT:
            return check_and_convert_value(value, str, factor.defaultValue)
        elif factor.type == NUMBER:
            return Decimal(value)
        elif factor_type == DATETIME:
            return convert_datetime(value)
        elif factor_type == BOOLEAN:
            return bool(value)
        elif factor_type == SEQUENCE:
            return int(value)
        elif factor_type == YEAR:
            return int(value)
        elif factor_type == MONTH:
            return int(value)
        elif factor_type == TIME:
            return arrow.get(value).datetime.replace(tzinfo=None)
        elif factor_type == DATE:
            return convert_date(value)
        else:
            return value
    except Exception as e:
        log.exception(e)
        raise TypeError("value are allowed {} for factor_type {}".format(value, factor_type))


def check_and_convert_value(value, type_class, type_text, default_):
    if value is None:
        if default_ is None:
            if type_text == "text":
                return ""
            elif type_text == "number" or type_text == "unsigned":
                return 0
        else:
            return default_
    if isinstance(value, type_class):
        return value
    else:
        if isinstance(value, str):
            if type_text == "number":
                pattern = re.compile(r'[\d+.]', re.I)
                if re.match(pattern, value.strip(), flags=0):
                    return Decimal(value)

            if type_text == "date":
                pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$', re.I)
                if re.match(pattern, value.strip(), flags=0):
                    return arrow.get(value).date()

            if type_text == "datetime":
                pattern = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', re.I)
                if re.match(pattern, value.strip(), flags=0):
                    return arrow.get(value).datetime.replace(tzinfo=None)

        raise TypeError("the value is not match type")
'''


def get_variable_with_func_pattern(name, context):
    variable_name_list = name.split(".&")
    if variable_name_list[0] in context:
        if isinstance(context[variable_name_list[0]], list):
            if variable_name_list[1] == "sum":
                return sum(context[variable_name_list[0]])
            elif variable_name_list[1] == "count":
                return len(context[variable_name_list[0]])
            else:
                raise ValueError("the function is not support")
        else:
            raise ValueError("the variable is not list")


def get_variable_with_dot_pattern(name, context):
    variable_name_list = name.split(".")
    if variable_name_list[0] in context:
        variable = flatten(
            {variable_name_list[0]: context[variable_name_list[0]]})
        # return variable[name]
        return variable.get(name, None)


def flatten(d_):
    out = {}
    for key, val in d_.items():
        if isinstance(val, dict):
            val = [val]
        if isinstance(val, list):
            for sub_dict in val:
                deeper = flatten(sub_dict).items()
                for key2, val2 in deeper:
                    if out.get(key + '.' + key2):
                        if isinstance(out.get(key + '.' + key2), list):
                            if isinstance(val2, list):
                                out[key + '.' + key2].extend(val2)
                            else:
                                out[key + '.' + key2].append(val2)
                        else:
                            values = [out[key + '.' + key2], val2]
                            out[key + '.' + key2] = values
                    else:
                        out[key + '.' + key2] = val2

        else:
            out[key] = val
    return out
