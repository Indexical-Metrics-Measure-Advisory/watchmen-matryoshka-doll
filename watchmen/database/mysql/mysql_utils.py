import json

from sqlalchemy import JSON


def parse_obj(base_model, result, table):
    model = base_model()
    for attr, value in model.__dict__.items():
        if attr[:1] != '_':
            if isinstance(table.c[attr.lower()].type, JSON):
                if attr == "on":
                    if result[attr] is not None:
                        setattr(model, attr, json.loads(result[attr.lower()]))
                    else:
                        setattr(model, attr, None)
                else:
                    if result[attr.lower()] is not None:
                        setattr(model, attr, json.loads(result[attr.lower()]))
                    else:
                        setattr(model, attr, None)
            else:
                setattr(model, attr, result[attr.lower()])

    # print(model)
    return base_model.parse_obj(model)
