from watchmen.pipeline.core.parameter.parse_parameter import parse_parameter


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
        current_value_ = parse_parameter(source, current_data, variables)

        if arithmetic is None or arithmetic == "none":  # mean AS IS
            result = {target_factor.name: current_value_}
        elif arithmetic == "sum":
            previous_value_ = parse_parameter(source, previous_data, variables)
            if previous_value_ is None:
                value_ = current_value_
            elif current_value_ > previous_value_:
                value_ = current_value_ - previous_value_
            else:
                value_ = previous_value_ - current_value_
            result = {target_factor.name: {"$sum": value_}}
            having_aggregate_functions = True
        elif arithmetic == "count":
            result = {target_factor.name: {"$count": 1}}
            having_aggregate_functions = True
        elif arithmetic == "avg":
            result = {target_factor.name: {"$avg": current_value_}}
            having_aggregate_functions = True

        mappings_results.update(result)

    return mappings_results, having_aggregate_functions


def get_factor(factor_id, target_topic):
    for factor in target_topic.factors:
        if factor.factorId == factor_id:
            return factor
