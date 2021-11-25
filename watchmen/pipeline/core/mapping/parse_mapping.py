from model.model.topic.factor import Factor
from model.model.topic.topic import Topic

from watchmen.pipeline.core.parameter.parse_parameter import parse_parameter
from watchmen.pipeline.core.parameter.utils import check_and_convert_value_by_factor


def parse_mappings(mappings, target_topic, previous_data, current_data, variables):
    having_aggregate_functions = False  # initial aggregate flag
    mappings_results = {}
    for mapping in mappings:
        if mapping.arithmetic is not None or mapping.arithmetic != "none":
            having_aggregate_functions = True  # confirm aggregation function in mapping, need concurrent control

        target_factor = get_factor(mapping.factorId, target_topic)
        arithmetic = mapping.arithmetic

        result = None
        source = mapping.source
        current_value_ = check_and_convert_value_by_factor(target_factor,
                                                           parse_parameter(source, current_data, variables))

        if arithmetic is None or arithmetic == "none":  # mean AS IS
            result = {target_factor.name: current_value_}
        elif arithmetic == "sum":
            previous_value_ = check_and_convert_value_by_factor(target_factor,
                                                                parse_parameter(source, previous_data, variables))
            if previous_value_ is None:
                previous_value_ = 0
            value_ = current_value_ - previous_value_
            result = {target_factor.name: {"_sum": value_}}
            having_aggregate_functions = True
        elif arithmetic == "count":
            if previous_data is None:
                result = {target_factor.name: {"_count": 1}}
            else:
                result = {target_factor.name: {"_count": 0}}
            having_aggregate_functions = True
        elif arithmetic == "avg":
            result = {target_factor.name: {"_avg": current_value_}}
            having_aggregate_functions = True

        mappings_results.update(result)
    # print(mappings_results)
    return mappings_results, having_aggregate_functions


def get_factor(factor_id, target_topic: Topic) -> Factor:
    for factor in target_topic.factors:
        if factor.factorId == factor_id:
            return factor
