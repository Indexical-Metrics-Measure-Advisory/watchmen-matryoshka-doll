from __future__ import annotations

from typing import List

from model.model.report.column import Operator

from watchmen.pipeline.core.case.model.parameter import Parameter, ParameterJoint
from watchmen.pipeline.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def _parse_parameter(parameter_: Parameter):
    if parameter_.kind == "topic":
        topic = get_topic_by_id(parameter_.topicId)
        # topic_name = build_collection_name(topic.name)
        factor = get_factor(parameter_.factorId, topic)
        return f'${factor.name}'
    elif parameter_.kind == 'constant':
        return parameter_.value
    elif parameter_.kind == 'computed':
        if parameter_.type == Operator.add:
            result = None
            for item in parameter_.parameters:
                if result:
                    result = {"$add": [result, _parse_parameter(item)]}
                else:
                    result = _parse_parameter(item)
            return result
        elif parameter_.type == Operator.subtract:
            result = None
            for item in parameter_.parameters:
                if result:
                    result = {"$subtract": [result, _parse_parameter(item)]}
                else:
                    result = _parse_parameter(item)
            return result
        elif parameter_.type == Operator.multiply:
            result = None
            for item in parameter_.parameters:
                if result:
                    result = {"$multiply": [result, _parse_parameter(item)]}
                else:
                    result = _parse_parameter(item)
            return result
        elif parameter_.type == Operator.divide:
            result = None
            for item in parameter_.parameters:
                if result:
                    result = {"$divide": [result, _parse_parameter(item)]}
                else:
                    result = _parse_parameter(item)
            return result
        elif parameter_.type == Operator.modulus:
            result = None
            for item in parameter_.parameters:
                if result:
                    result = {"$mod": [result, _parse_parameter(item)]}
                else:
                    result = _parse_parameter(item)
            return result
        elif parameter_.type == "case-then":
            return parse_mongo_case_then(parameter_.parameters)
        else:
            raise Exception("operator is not supported")


def parse_storage_case_then(parameters_: List[Parameter]) -> any:
    return parse_mongo_case_then(parameters_)


def parse_mongo_case_then(parameters: List[Parameter]) -> any:
    branches = []
    default_ = {}
    for param in parameters:
        if param.on:
            condition = _parse_parameter_joint(param.on)
            value = _parse_parameter(param)
            branches.append({"case": condition, "then": value})
        else:
            default_ = _parse_parameter(param)
    switch = {'$switch:': {'branches': branches, 'default': default_}}
    return switch


def _parse_parameter_joint(joint: ParameterJoint):
    results = []
    if joint.jointType is not None:
        if joint.jointType == "and":
            for filter_ in joint.filters:
                results.append(_parse_parameter_joint(filter_))
            return {"$and": results}
        elif joint.jointType == "or":
            for filter_ in joint.filters:
                results.append(_parse_parameter_joint(filter_))
            return {"$or": results}
    else:
        for filter_ in joint.filters:
            left = _parse_parameter(filter_.left)
            operator_ = filter_.operator
            right = _parse_parameter(filter_.right)
            if left.startswith("$"):
                left = left.lstrip("$")
            if operator_ == "equals":
                return {left: {"$eq": right}}
            elif operator_ == "not-equals":
                return {left: {"$ne": right}}
            elif operator_ == 'empty':
                return {left: {"$eq": ""}}
            elif operator_ == 'not-empty':
                return {left: {"$ne": ""}}
            elif operator_ == "more":
                return {left: {"$gt": right}}
            elif operator_ == "more-equals":
                return {left: {"$gte": right}}
            elif operator_ == "less":
                return {left: {"$lt": right}}
            elif operator_ == "less-equals":
                return {left: {"$lte": right}}
            elif operator_ == 'in':
                return {left: {"$in": right}}
            elif operator_ == 'not-in':
                return {left: {"$nin": right}}
            else:
                raise Exception("operator is not supported")
