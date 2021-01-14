from watchmen.topic.factor.factor import Factor
from watchmen.topic.topic import Topic


def check_condition(operator, left_value, right_value):
    if operator == "equals":
        return left_value == right_value
    elif operator == "not-equals":
        return left_value != right_value
    elif operator == "less":
        return left_value<right_value
    elif operator == "less-equals":
        return left_value<=right_value
    elif operator == "more":
        return left_value > right_value
    elif operator == "more-equals":
        return left_value >= right_value
    else:
        raise Exception("NotImplemented:", operator)


def convert_factor_type(value, factor_type):
    if factor_type == "Text":
        return str(value)
    if factor_type == "Number":
        # TODO process number type
        return float(value)
    else:
        return value


def get_factor(factor_id, target_topic:Topic):

    for factor in target_topic.factors:
        if factor.factorId == factor_id:
            return factor


def get_value(factor: Factor,data):
    value = data[factor.name]
    return convert_factor_type(value, factor.type)