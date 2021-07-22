import pandas as pd

from watchmen.pipeline.core.case.model.parameter import Parameter, ParameterJoint
from watchmen.pipeline.core.parameter.utils import cal_factor_value, get_variable_with_func_pattern, \
    get_variable_with_dot_pattern, convert_datetime, check_and_convert_value_by_factor
from watchmen.pipeline.utils.units_func import get_factor
from watchmen.report.model.column import Operator
from watchmen.topic.topic import Topic


def parse_parameter(parameter_: Parameter, current_data, variables, pipeline_topic: Topic, target_topic: Topic):
    """
    the case-then can only be used in one side in expression
    """
    if parameter_.kind == "topic":
        if parameter_.topicId == pipeline_topic.topicId:
            factor = get_factor(parameter_.factorId, pipeline_topic)
            return {"value": check_and_convert_value_by_factor(factor, cal_factor_value(current_data, factor)),
                    "position": "right"}
        elif parameter_.topicId == target_topic.topicId:
            factor = get_factor(parameter_.factorId, target_topic)
            factor_name = factor.name
            return {"value": factor_name, "factor": factor, "position": "left"}
    elif parameter_.kind == 'constant':
        if parameter_.value is None:
            return {"value": None, "position": "right"}
        elif parameter_.value == '':
            return {"value": None, "position": "right"}
        elif not parameter_.value:
            return {"value": None, "position": "right"}
        elif parameter_.value.startswith("{"):
            constant_variable = parameter_.value.replace("{", "").replace("}", "")
            if ".&" in constant_variable:
                return {"value": get_variable_with_func_pattern(constant_variable, variables),
                        "position": "right"}
            elif "." in constant_variable:
                return {"value": get_variable_with_dot_pattern(constant_variable, variables),
                        "position": "right"}
            else:
                if constant_variable in variables and variables[constant_variable] is not None:
                    return {"value": variables[constant_variable], "position": "right"}
                else:
                    return {"value": None, "position": "right"}
        elif "," in parameter_.value:
            value_ = parameter_.value.split(",")
            new_value_ = []
            for v in value_:
                if v.isdigit():
                    new_value_.append(int(v))
                else:
                    new_value_.append(v)
            return {"value": new_value_, "position": "right"}
        else:
            return {"value": parameter_.value, "position": "right"}
    elif parameter_.kind == 'computed':
        if parameter_.type == Operator.add:
            result = None
            for item in parameter_.parameters:
                if item.kind == "topic" and item.topicId != pipeline_topic.topicId:
                    raise Exception("only pipeline topic factor can be used in add operator")
                if result:
                    next_ = parse_parameter(item, current_data, variables, pipeline_topic, target_topic)
                    result = {"value": result["value"] + next_["value"], "position": "right"}
                else:
                    result = parse_parameter(item, current_data, variables, pipeline_topic, target_topic)
            return result
        elif parameter_.type == Operator.subtract:
            result = None
            for item in parameter_.parameters:
                if item.kind == "topic" and item.topicId != pipeline_topic.topicId:
                    raise Exception("only pipeline topic factor can be used in subtract operator")
                if result:
                    next_ = parse_parameter(item, current_data, variables, pipeline_topic, target_topic)
                    result = {"value": result["value"] - next_["value"], "position": "right"}
                else:
                    result = parse_parameter(item, current_data, variables, pipeline_topic, target_topic)
            return result
        elif parameter_.type == Operator.multiply:
            result = None
            for item in parameter_.parameters:
                if item.kind == "topic" and item.topicId != pipeline_topic.topicId:
                    raise Exception("only pipeline topic factor can be used in multiply operator")
                if result:
                    next_ = parse_parameter(item, current_data, variables, pipeline_topic, target_topic)
                    result = {"value": result["value"] * next_["value"], "position": "right"}
                else:
                    result = parse_parameter(item, current_data, variables, pipeline_topic, target_topic)
            return result
        elif parameter_.type == Operator.divide:
            result = None
            for item in parameter_.parameters:
                if item.kind == "topic" and item.topicId != pipeline_topic.topicId:
                    raise Exception("only pipeline topic factor can be used in divide operator")
                if result:
                    next_ = parse_parameter(item, current_data, variables, pipeline_topic, target_topic)
                    result = {"value": result["value"] / next_["value"], "position": "right"}
                else:
                    result = parse_parameter(item, current_data, variables, pipeline_topic, target_topic)
            return result
        elif parameter_.type == Operator.modulus:
            result = None
            for item in parameter_.parameters:
                if item.kind == "topic" and item.topicId != pipeline_topic.topicId:
                    raise Exception("only pipeline topic factor can be used in modulus operator")
                if result:
                    next_ = parse_parameter(item, current_data, variables, pipeline_topic, target_topic)
                    result = {"value": result["value"] % next_["value"], "position": "right"}
                else:
                    result = parse_parameter(item, current_data, variables, pipeline_topic, target_topic)
            return result
        elif parameter_.type == "year-of":
            result = parse_parameter(parameter_.parameters[0], current_data, variables, pipeline_topic, target_topic)
            value_ = result["value"]
            return {"value": convert_datetime(value_).year, "position": "right"}
        elif parameter_.type == "month-of":
            result = parse_parameter(parameter_.parameters[0], current_data, variables, pipeline_topic, target_topic)
            value_ = result["value"]
            return {"value": convert_datetime(value_).month, "position": "right"}
        elif parameter_.type == "week-of-year":
            result = parse_parameter(parameter_.parameters[0], current_data, variables, pipeline_topic, target_topic)
            value_ = result["value"]
            return {"value": convert_datetime(value_).isocalendar()[1], "position": "right"}
        elif parameter_.type == "day-of-week":
            result = parse_parameter(parameter_.parameters[0], current_data, variables, pipeline_topic, target_topic)
            value_ = result["value"]
            return {"value": convert_datetime(value_).weekday(), "position": "right"}
        elif parameter_.type == "day-of-month":
            result = parse_parameter(parameter_.parameters[0], current_data, variables, pipeline_topic, target_topic)
            value_ = result["value"]
            return {"value": __week_number_of_month(convert_datetime(value_).date()), "position": "right"}
        elif parameter_.type == "quarter-of":
            result = parse_parameter(parameter_.parameters[0], current_data, variables, pipeline_topic, target_topic)
            value_ = result["value"]
            quarter = pd.Timestamp(convert_datetime(value_)).quarter
            return {"value": quarter, "position": "right"}
        elif parameter_.type == "half-year-of":
            result = parse_parameter(parameter_.parameters[0], current_data, variables, pipeline_topic, target_topic)
            value_ = result["value"]
            month = convert_datetime(value_).month
            if month <= 6:
                return {"value": 1, "position": "right"}
            else:
                return {"value": 2, "position": "right"}
        elif parameter_.type == "day-of-month":
            result = parse_parameter(parameter_.parameters[0], current_data, variables, pipeline_topic, target_topic)
            value_ = result["value"]
            return {"value": convert_datetime(value_).day, "position": "right"}
        elif parameter_.type == "case-then":
            parameters_ = parameter_.parameters
            when_ = []
            else_ = None
            for param in parameters_:
                if param.on is not None:
                    condition = parse_parameter_joint(param.on, current_data, variables, pipeline_topic, target_topic)
                    value_ = parse_parameter(param, current_data, variables, pipeline_topic, target_topic)
                    when_.append({"$when": condition, "$then": value_})
                else:
                    else_ = parse_parameter(param, current_data, variables, pipeline_topic, target_topic)

            return {"value": {"$case": {"$clause": when_, "$else": else_}},
                    "position": "left"}
        else:
            raise Exception("operator is not supported")


def parse_parameter_joint(joint: ParameterJoint, current_data, variables, pipeline_topic: Topic, target_topic: Topic):
    where_ = {}
    results = []
    if joint.jointType is not None:
        if joint.jointType == "and":
            for filter_ in joint.filters:
                results.append(parse_parameter_joint(filter_, current_data, variables, pipeline_topic, target_topic))
            where_ = {"and": results}
            return where_
        elif joint.jointType == "or":
            for filter_ in joint.filters:
                results.append(parse_parameter_joint(filter_, current_data, variables, pipeline_topic, target_topic))
            where_ = {"or": results}
            return where_
    else:
        left_expr_item = parse_parameter(joint.left, current_data, variables, pipeline_topic, target_topic)
        operator_ = joint.operator
        right_expr_item = parse_parameter(joint.right, current_data, variables, pipeline_topic, target_topic)

        if left_expr_item["position"] == right_expr_item["position"]:
            raise Exception("the configuration of by have error, please check")

        if left_expr_item["position"] == "left":
            name = left_expr_item["value"]
            factor = left_expr_item.get("factor", None)
        else:
            value = left_expr_item["value"]

        if right_expr_item["position"] == "left":
            name = right_expr_item["value"]
            factor = right_expr_item.get("factor", None)
        else:
            value = right_expr_item["value"]

        if factor is not None:
            if isinstance(value, list) and factor.type != "array":
                new_value_ = []
                for el in value:
                    new_value_.append(check_and_convert_value_by_factor(factor, el))
                value = new_value_
            else:
                value = check_and_convert_value_by_factor(factor, value)

        if operator_ == "equals":
            return {name: {"=": value}}
        elif operator_ == "not-equals":
            return {name: {"!=": value}}
        elif operator_ == "more":
            return {name: {">": value}}
        elif operator_ == "more-equals":
            return {name: {">=": value}}
        elif operator_ == "less":
            return {name: {"<": value}}
        elif operator_ == "less-equals":
            return {name: {"<=": value}}
        elif operator_ == 'in':
            return {name: {"in": value}}
        elif operator_ == 'not-in':
            return {name: {"not-in": value}}
        elif operator_ == "empty":
            return {name: {"=": None}}
        else:
            raise Exception("operator is not supported")


def __week_number_of_month(date_value):
    return date_value.isocalendar()[1] - date_value.replace(day=1).isocalendar()[1] + 1


def check_calculate_scope(parameter_: Parameter, pipeline_topic: Topic, target_topic: Topic, condition: str) -> bool:
    if parameter_.kind == "topic":
        if condition == "source":
            if parameter_.topicId != pipeline_topic.topicId:
                # raise Configurationerror("only pipeline topic factor can be in this calculation")
                return False
        if condition == "target":
            if parameter_.topicId != target_topic.topicId:
                # raise Configurationerror("only target topic factor can be in this calculation")
                return False
    elif parameter_.kind == 'computed':
        for item in parameter_.parameters:
            return check_calculate_scope(item, pipeline_topic, target_topic, condition)


class Configurationerror(RuntimeError):
    def __init__(self, arg):
        self.args = arg
