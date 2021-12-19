import datetime
from collections import deque
from enum import Enum

from model.model.topic.factor import Factor
from model.model.topic.topic import Topic

from watchmen_boot.guid.snowflake import get_surrogate_key
from watchmen.topic.service.topic_service import create_topic_schema


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


def create_raw_topic_v3(code, data, current_user):
    topic = Topic()
    topic.topicId = get_surrogate_key()
    topic.tenantId = current_user.tenantId
    topic.name = code
    topic.type = "raw"
    topic.factors = []
    queue = deque([])
    rs = Relationship()
    if type(data) == list:
        for record in data:
            model: dict = {"root": record}
            queue.append(model)
        create_factors(queue, topic, rs)
        mp = rs.get_mapping()
        parent = []
        child = mp.get("root", [])
        generate_surrogate_key("root", parent, child, mp, topic)
        create_topic_schema(topic)
    else:
        raise ValueError("the data must be array")


def create_factors(queue, topic, rs):
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
                            rs.add_relationship(key, factor_name)
                        else:
                            queue.append({key + "." + factor_name: factor_value[0]})
                            rs.add_relationship(key, key + "." + factor_name)
                    if factor_value_type == ValueType.DICT:
                        if key == "root":
                            queue.append({factor_name: factor_value})
                            rs.add_relationship(key, factor_name)
                        else:
                            queue.append({key + "." + factor_name: factor_value})
                            rs.add_relationship(key, key + "." + factor_name)
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
                            rs.add_relationship(key, factor_name)
                        else:
                            queue.append({key + "." + factor_name: factor_value[0]})
                            rs.add_relationship(key, key + "." + factor_name)
                    if factor_value_type == ValueType.DICT:
                        if key == "root":
                            queue.append({factor_name: factor_value})
                            rs.add_relationship(key, factor_name)
                        else:
                            queue.append({key + "." + factor_name: factor_value})
                            rs.add_relationship(key, key + "." + factor_name)
    if len(queue) != 0:
        create_factors(queue, topic, rs)


class Relationship:

    def __init__(self):
        self.mapping = {}

    def add_relationship(self, current, child):
        child_list = self.mapping.get(current, None)
        if child_list:
            if child in child_list:
                pass
            else:
                child_list.append(child)
        else:
            self.mapping[current] = [child]

    def get_mapping(self):
        return self.mapping


def generate_surrogate_key(current, parent, child, mp, topic):
    if current == "root":
        parent.append("root")
        for l_node in child:
            next_ = mp.get(l_node, None)
            if next_:
                generate_surrogate_key(l_node, parent, next_, mp, topic)
    else:
        factor = Factor()
        factor.name = current + "." + "aid_me"
        factor.label = current + "." + "aid_me"
        factor.type = "number"
        factor.factorId = get_surrogate_key()
        topic.factors.append(factor)
        duplicate = []
        for p_node in reversed(parent):
            if p_node != "root":
                factor = Factor()
                if "." in p_node:
                    name_ = p_node.rsplit(".", 1)[1]
                else:
                    name_ = p_node
                if check_duplicate_aid_name(name_, duplicate):
                    distance = current.count(".") - p_node.count(".")
                    factor.name = current + "." + "aid_" + name_ + "_" + str(distance)
                    factor.label = current + "." + "aid_" + name_ + "_" + str(distance)
                else:
                    factor.name = current + "." + "aid_" + name_
                    factor.label = current + "." + "aid_" + name_
                    duplicate.append(name_)
                factor.type = "number"
                factor.factorId = get_surrogate_key()
                topic.factors.append(factor)
        parent.append(current)
        for l_node in child:
            next_ = mp.get(l_node, None)
            if next_:
                generate_surrogate_key(l_node, parent, next_, mp, topic)
            else:
                generate_surrogate_key(l_node, parent, [], mp, topic)
        parent.remove(current)


def check_duplicate_aid_name(name, duplicate):
    if name in duplicate:
        return True
