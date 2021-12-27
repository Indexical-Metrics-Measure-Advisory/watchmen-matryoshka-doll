from datetime import datetime
from decimal import Decimal

import arrow
from model.model.topic.factor import Factor


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


def check_and_convert_value_by_factor(factor: Factor, value):
    try:
        if value is None:
            return None
        if value == "" or value == '':
            return None
        if factor is None:
            raise ValueError("factor can not be none, in check_and_convert_value_by_factor function")
        elif factor.type == "text":
            return str(value)
        elif factor.type == "number" or factor.type == "unsigned":
            return Decimal(value)
        elif factor.type == "datetime":
            return convert_datetime(value)
        elif factor.type == "year":
            return int(value)
        elif factor.type == "month":
            return int(value)
        elif factor.type == "time":
            return arrow.get(value).datetime.replace(tzinfo=None)
        elif factor.type == "date":
            return convert_date(value)
        else:
            return value
    except Exception as e:
        raise TypeError(
            "value \"{0}\" is not allowed for factor \"{1}\" because of factor_type is \"{2}\"".format(value,
                                                                                                       factor.name,
                                                                                                       factor.type))


def get_variable_with_func_pattern(name, variable_):
    variable_name_list = name.split(".&")
    if variable_name_list[0] in variable_:
        if isinstance(variable_[variable_name_list[0]], list):
            if variable_name_list[1] == "sum":
                return sum(variable_[variable_name_list[0]])
            elif variable_name_list[1] == "count":
                return len(variable_[variable_name_list[0]])
            else:
                raise ValueError("the function is not support")
        else:
            raise ValueError("the variable is not list")


def get_variable_with_dot_pattern(name, variable_):
    variable_name_list = name.split(".")
    if variable_name_list[0] in variable_:
        variable = flatten(
            {variable_name_list[0]: variable_[variable_name_list[0]]})
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
