from watchmen.pipeline.core.parameter.utils import check_and_convert_value_by_factor
from watchmen.topic.factor.factor import Factor


def get_flatten_field(data: dict, factors: dict):
    flatten_fields = {}
    for factor in factors:
        factor_obj = Factor.parse_obj(factor)
        if factor_obj.flatten:
            key = factor_obj.name
            value = check_and_convert_value_by_factor(factor_obj, data.get(key, None))
            flatten_fields[key.lower()] = value
    return flatten_fields
