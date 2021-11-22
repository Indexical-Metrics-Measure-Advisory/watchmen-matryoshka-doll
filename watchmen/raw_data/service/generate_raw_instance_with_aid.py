from pydantic import BaseModel

from watchmen.common.snowflake.snowflake import get_int_surrogate_key
from watchmen.topic.storage.topic_schema_storage import get_topic_by_name


def create_raw_topic_instance(code, data, current_user):
    nodes = get_nodes(code, current_user)
    context_ = {}
    list_dictionary("root", data, nodes, context_)


def list_dictionary(code, data_, nodes, context_):
    if isinstance(data_, list):
        for item_ in data_:
            list_dictionary(code, item_, nodes, context_)
    elif isinstance(data_, dict):
        if code in nodes:
            node_info = nodes.get(code)
            for key in node_info.aid_keys:
                if key == "aid_me":
                    sid_ = get_int_surrogate_key()
                    data_[key] = sid_
                    context_[code] = sid_
                else:
                    num_ = key.count("_")
                    if num_ == 1:
                        p_key = key.rsplit("_", 1)[1]
                        re = code.rfind(p_key, 0, len(code))
                        if re != -1:
                            p_code = code[0:re + len(p_key)]
                            pid_ = context_.get(p_code)
                            data_[key] = pid_
                        else:
                            raise "{} is not parent of {}".format(p_key, code)
                    elif num_ == 2:
                        distance = key.rsplit("_", 1)[1]
                        code_list = code.split(".")
                        len_ = len(code_list)
                        new_code_list = []
                        for i in range(len_):
                            if i < (len_ - int(distance)):
                                new_code_list.append(code_list[i])
                        new_code = ".".join(new_code_list)
                        pid_ = context_.get(new_code)
                        data_[key] = pid_
        for key, value in data_.items():
            if code == "root":
                list_dictionary(key, value, nodes, context_)
            else:
                list_dictionary(code + "." + key, value, nodes, context_)
    else:
        pass


def get_nodes(code, current_user):
    topic = get_topic_by_name(code, current_user)
    factors = topic.factors
    nodes = {}
    for item in factors:
        if ".aid_" in item.name:
            factor_name = item.name
            list_ = factor_name.rsplit(".", 1)
            node_name = list_[0]
            key_name = list_[1]
            node_info = nodes.get(node_name, None)
            if node_info:
                node_info.aid_keys.append(key_name)
            else:
                node_info = NodeInfo(**{"name": node_name,
                                        "parent": [],
                                        "child": [],
                                        "aid_keys": [key_name]})
                nodes[node_name] = node_info
                if "." in node_name:
                    num_ = node_name.count(".")
                    parent_name = node_name
                    for i in range(num_):
                        parent_name = parent_name.rsplit(".", 1)[0]
                        parent_node_info = nodes.get(parent_name, None)
                        if parent_node_info:
                            parent_node_info.child.append(node_info)
                        else:
                            parent_node_info = NodeInfo(**{"name": parent_name,
                                                           "parent": [],
                                                           "chlid": [],
                                                           "aid_keys": []})
                            nodes[parent_name] = parent_node_info
                        node_info.parent.append(parent_node_info)
    return nodes


class NodeInfo(BaseModel):
    name: str = None
    parent: list = None
    child: list = None
    aid_keys: list = None
