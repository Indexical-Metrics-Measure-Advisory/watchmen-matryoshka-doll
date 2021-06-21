from sqlalchemy.orm import Session

from watchmen.common.mysql.mysql_engine import engine
from watchmen.common.storage.utils.table_utils import get_primary_key


def parse_obj(base_model, result):
    model = base_model()
    for attr, value in model.__dict__.items():
        if attr[:1] != '_':
            setattr(model, attr, getattr(result, attr))
    return model


def count_table(table_name):
    primary_key = get_primary_key(table_name)
    session = Session(engine, future=True)
    stmt = 'SELECT count(%s) AS count FROM %s' % (primary_key, table_name)
    result = session.execute(stmt)
    for row in result:
        return row[0]
