import datetime
from collections import deque
from enum import Enum

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.topic.factor.factor import Factor
from watchmen.topic.service.topic_service import create_topic_schema
from watchmen.topic.topic import Topic


class ValueType(str, Enum):
    INT = "number"
    STR = "text"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    LIST = "array"
    DICT = "object"
    REF = "ref"
    ANY = "any"


def check_value_type(value):
    if isinstance(value, int):
        return ValueType.INT
    if isinstance(value, float):
        return ValueType.INT
    if isinstance(value, str):
        return ValueType.STR
    if isinstance(value, type(True)) or isinstance(value, type(False)):
        return ValueType.BOOLEAN
    if isinstance(value, datetime.date):
        return ValueType.DATE
    if isinstance(value, datetime.datetime):
        return ValueType.DATETIME
    if isinstance(value, list):
        return ValueType.LIST
    if isinstance(value, dict):
        return ValueType.DICT
    return ValueType.ANY


def check_factor_in_topic(prefix, factor_name, topic):
    if prefix != "root":
        name_ = prefix + "." + factor_name
    else:
        name_ = factor_name
    for factor in topic.factors:
        if name_ == factor.name:
            return True, factor
    return False, None


def check_list_element_type_is_object(value_list):
    if isinstance(value_list, list):
        if len(value_list) == 0:
            return False
        for el in value_list:
            if not isinstance(el, dict):
                return False
        return True
    else:
        return False


def create_raw_topic(code, data, current_user):
    topic = Topic()
    topic.topicId = get_surrogate_key()
    topic.tenantId = current_user.tenantId
    topic.name = code
    topic.type = "raw"
    topic.factors = []
    queue = deque([])
    if type(data) == list:
        for record in data:
            model: dict = {"root": record}
            queue.append(model)
    create_factors(queue, topic)
    create_topic_schema(topic)


def create_factors(queue, topic):
    model = queue.popleft()
    for key, value in model.items():
        if not isinstance(value, dict):
            raise TypeError("create factors need the dict type value, \'{0}\' is not dict".format(value))
        else:
            for factor_name, factor_value in value.items():
                result_tup = check_factor_in_topic(key, factor_name, topic)
                if result_tup[0]:
                    factor = result_tup[1]
                    factor_value_type = check_value_type(factor_value)

                    if factor_value_type != ValueType.ANY and factor.type == ValueType.ANY:
                        factor.type = factor_value_type
                    elif factor_value_type != ValueType.ANY and factor.type != ValueType.ANY and \
                            factor_value_type != factor.type:
                        raise Exception("factor {0} has different value type: {1} and {2}".format(factor.name,
                                                                                                  factor_value_type,
                                                                                                  factor.type))

                    if (factor_value_type == ValueType.LIST and check_list_element_type_is_object(
                            factor_value)):
                        if key == "root":
                            queue.append({factor_name: factor_value[0]})
                        else:
                            queue.append({key + "." + factor_name: factor_value[0]})
                    if factor_value_type == ValueType.DICT:
                        if key == "root":
                            queue.append({factor_name: factor_value})
                        else:
                            queue.append({key + "." + factor_name: factor_value})
                else:
                    factor_value_type = check_value_type(factor_value)
                    factor = Factor()
                    factor.name = factor_name if key == "root" else key + "." + factor_name
                    factor.label = factor_name if key == "root" else key + "." + factor_name
                    factor.type = factor_value_type
                    factor.factorId = get_surrogate_key()
                    topic.factors.append(factor)
                    if factor_value_type == ValueType.LIST and check_list_element_type_is_object(factor_value):
                        if key == "root":
                            queue.append({factor_name: factor_value[0]})
                        else:
                            queue.append({key + "." + factor_name: factor_value[0]})
                    if factor_value_type == ValueType.DICT:
                        if key == "root":
                            queue.append({factor_name: factor_value})
                        else:
                            queue.append({key + "." + factor_name: factor_value})
    if len(queue) != 0:
        create_factors(queue, topic)
