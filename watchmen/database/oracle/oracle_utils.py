import json

from sqlalchemy import CLOB, text

from watchmen.database.oracle.oracle_engine import engine
from watchmen.database.storage.utils.table_utils import get_primary_key


def parse_obj(base_model, result, table):
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


def count_table(table_name):
    primary_key = get_primary_key(table_name)
    stmt = 'SELECT count(%s) AS count FROM %s' % (primary_key, table_name)
    with engine.connect() as conn:
        cursor = conn.execute(text(stmt)).cursor
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        result = cursor.fetchone()
    return result['COUNT']


def count_topic_data_table(table_name):
    stmt = 'SELECT count(%s) AS count FROM %s' % ('id_', table_name)
    with engine.connect() as conn:
        cursor = conn.execute(text(stmt)).cursor
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        result = cursor.fetchone()
    return result['COUNT']
