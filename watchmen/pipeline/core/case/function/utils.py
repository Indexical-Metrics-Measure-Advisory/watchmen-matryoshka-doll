import re

'''
for constant usage

'''

DOT = "."
FUNC = ".&"
AMP = "&"


def parse_constant_expression(value: str) -> list:
    pattern = re.compile(r'(\{[a-zA-Z0-9_.&]+\})', re.I)
    return pattern.split(value)


def get_variable_with_dot_pattern(name, context):
    variable_name_list = name.split(DOT)
    if variable_name_list[0] in context:
        variable = flatten({variable_name_list[0]: context[variable_name_list[0]]})
        return variable.get(name, None)


def get_variable_with_func_pattern(name, context):
    variable_name_list = name.split(FUNC)
    if variable_name_list[0] in context:
        if isinstance(context[variable_name_list[0]], list):
            if variable_name_list[1] == "sum":
                return sum(context[variable_name_list[0]])
            elif variable_name_list[1] == "count":
                return len(context[variable_name_list[0]])
            else:
                raise ValueError("the function is not support")
        else:
            raise ValueError("the variable is not list")


def flatten(d_):
    out = {}
    for key, val in d_.items():
        if isinstance(val, dict):
            val = [val]
        if isinstance(val, list):
            for sub_dict in val:
                deeper = flatten(sub_dict).items()
                for key2, val2 in deeper:
                    if out.get(key + '.' + key2):
                        if isinstance(out.get(key + '.' + key2), list):
                            if isinstance(val2, list):
                                out[key + '.' + key2].extend(val2)
                            else:
                                out[key + '.' + key2].append(val2)
                        else:
                            values = [out[key + '.' + key2], val2]
                            out[key + '.' + key2] = values
                    else:
                        out[key + '.' + key2] = val2
        else:
            out[key] = val
    return out
