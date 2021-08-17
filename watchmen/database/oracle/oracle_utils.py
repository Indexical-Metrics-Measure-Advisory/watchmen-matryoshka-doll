import json

from sqlalchemy import CLOB


def parse_obj(self ,base_model, result, table):
    model = base_model()
    for attr, value in model.__dict__.items():
        if attr[:1] != '_':
            if isinstance(table.c[attr.lower()].type, CLOB):
                if attr == "on":
                    if result[attr] is not None:
                        setattr(model, attr, json.loads(result[attr]))
                    else:
                        setattr(model, attr, None)
                else:
                    if result[attr.upper()] is not None:
                        setattr(model, attr, json.loads(result[attr.upper()]))
                    else:
                        setattr(model, attr, None)
            else:
                setattr(model, attr, result[attr.upper()])
    return base_model.parse_obj(model)