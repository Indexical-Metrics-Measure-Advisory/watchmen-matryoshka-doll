from datetime import datetime

from watchmen.topic.factor.factor import Factor


# TODO constant for operator
def check_condition(operator, left_value, right_value):
    if operator == "equals":
        return left_value == right_value
    elif operator == "not-equals":
        return left_value != right_value
    elif operator == "less":
        return left_value < right_value
    elif operator == "less-equals":
        return left_value <= right_value
    elif operator == "more":
        return left_value > right_value
    elif operator == "more-equals":
        return left_value >= right_value
    else:
        raise Exception("NotImplemented:", operator)


def convert_factor_type(value, factor_type):
    if factor_type == "text":
        return str(value)
    elif factor_type == "number":
        # TODO process number type
        return float(value)
    elif factor_type == "datetime":
        return datetime.fromisoformat(value)
    elif factor_type == "boolean":
        return bool(value)
    elif factor_type == "sequence":
        return int(value)
    else:
        return value


def get_factor(factor_id, target_topic):
    for factor in target_topic.factors:
        if factor.factorId == factor_id:
            return factor


def get_factor_func(factor: Factor, data):
    # factor.
    pass


def get_value(factor: Factor, data):
    if factor.name in data:
        value = data[factor.name]
        return convert_factor_type(value, factor.type)
    elif factor.type == "number":
        return None
    elif factor.type == "text":
        return None
    else:
        return None
