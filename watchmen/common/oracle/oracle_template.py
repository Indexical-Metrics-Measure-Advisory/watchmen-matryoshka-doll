import logging
from operator import eq

from sqlalchemy import update, MetaData, Table, and_, or_, delete
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from watchmen.common.mysql.model.table_definition import get_table_model, get_primary_key, parse_obj, count_table
from watchmen.common.mysql.mysql_engine import engine
from watchmen.common.storage.storage_template import DataPage
from watchmen.common.utils.data_utils import build_data_pages
from watchmen.common.utils.data_utils import convert_to_dict

log = logging.getLogger("app." + __name__)

log.info("oralce template initialized")


def insert_one(one, model, name):
    table = get_table_model(name)
    session = Session(engine, future=True)
    stmt = insert(table)
    instance_dict: dict = convert_to_dict(one)
    values = {}
    for key, value in instance_dict.items():
        values[key] = value
    try:
        session.execute(stmt, values)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    return model.parse_obj(one)


def insert_all(data, model, name):
    metadata = MetaData()
    table = Table(name, metadata, autoload=True, autoload_with=engine)
    stmt = insert(table)
    value_list = []
    for item in data:
        instance_dict: dict = convert_to_dict(item)
        values = {}
        for key in table.c.keys():
            values[key] = instance_dict.get(key)
        value_list.append(values)
    with engine.connect() as conn:
        result = conn.execute(stmt, value_list)
        conn.commit()


def update_one(one, model, name) -> any:
    table = get_table_model(name)
    stmt = update(table)
    instance_dict: dict = convert_to_dict(one)
    primary_key = get_primary_key(name)
    stmt = stmt.where(eq(getattr(table, primary_key), instance_dict.get(primary_key)))
    values = {}
    for key, value in instance_dict.items():
        if key != get_primary_key(name):
            values[key] = value
    stmt = stmt.values(values)
    session = Session(engine, future=True)
    try:
        session.execute(stmt)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    return model.parse_obj(one)


def update_one(where, updates, model, name):
    table = get_table_model(name)
    stmt = update(table)
    stmt = stmt.where(build_where_expression(where))
    instance_dict: dict = convert_to_dict(updates)
    values = {}
    for key, value in instance_dict.items():
        if key != get_primary_key(name):
            values[key] = value
    stmt = stmt.values(values)
    session = Session(engine, future=True)
    try:
        session.execute(stmt)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    return model.parse_obj(updates)


def upsert(where, updates, model, name):
    table = get_table_model(name)
    instance_dict: dict = convert_to_dict(updates)
    stmt = insert(table)
    stmt = stmt.values(updates)
    stmt = stmt.on_duplicate_key_update(instance_dict)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()
    return model.parse_obj(updates)


def update_(where, updates, model, name):
    table = get_table_model(name)
    stmt = update(table)
    stmt = stmt.where(build_where_expression(where))
    instance_dict: dict = convert_to_dict(updates)
    values = {}
    for key, value in instance_dict.items():
        if key != get_primary_key(name):
            values[key] = value
    stmt = stmt.values(values)
    session = Session(engine, future=True)
    try:
        session.execute(stmt)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def delete_one(id: str, name: str):
    table = get_table_model(name)
    key = get_primary_key(name)
    stmt = delete(table).where(table.c.get(key) == id)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


def delete_(where, model, name):
    table = get_table_model(name)
    stmt = delete(table).where(where)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


def find_by_id(id, model, name):
    table = get_table_model(name)
    primary_key = get_primary_key(name)
    stmt = select(table).where(eq(getattr(table, primary_key), id))
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
    return parse_obj(model, result[0])


def find_one(where, model, name):
    table = get_table_model(name)
    stmt = select(table)
    stmt = stmt.where(build_where_expression(table, where))
    with engine.connect() as conn:
        result = conn.execute(stmt).first()
        conn.commit()
    return parse_obj(model, result[0])


def list_all(model, name):
    table = get_table_model(name)
    stmt = select(table)
    with engine.connect() as conn:
        res = conn.execute(stmt)
        conn.commit()
    result = []
    for row in res:
        for item in row:
            result.append(parse_obj(model, item))
    return result


def list_(where, model, name) -> list:
    table = get_table_model(name)
    stmt = select(table).where(where)
    with engine.connect() as conn:
        res = conn.execute(stmt)
        conn.commit()
    result = []
    for row in res:
        for item in row:
            result.append(parse_obj(model, item))
    return result


def page(sort, pageable, model, name) -> DataPage:
    count = count_table(name)
    table = get_table_model(name)
    stmt = select(table).order_by(sort)
    offset = pageable.pageSize * (pageable.pageNumber - 1)
    stmt = stmt.offset(offset).limit(pageable.pageSize)
    result = []
    with engine.connect() as conn:
        res = conn.execute(stmt)
        conn.commit()
    for row in res:
        for item in row:
            result.append(parse_obj(model, item))
    return build_data_pages(pageable, result, count)


def page(where, sort, pageable, model, name) -> DataPage:
    count = count_table(name)
    table = get_table_model(name)
    stmt = select(table).where(build_where_expression(where)).order_by(sort)
    offset = pageable.pageSize * (pageable.pageNumber - 1)
    stmt = stmt.offset(offset).limit(pageable.pageSize)
    result = []
    with engine.connect() as conn:
        res = conn.execute(stmt)
        conn.commit()
    for row in res:
        for item in row:
            result.append(parse_obj(model, item))
    return build_data_pages(pageable, result, count)


def build_where_expression(table, conditions):
    filters: list = []
    for key, value in conditions.item():
        if key == "$and":
            f = and_(*build_where_expression(value))
        elif key == "$or":
            f = or_(*build_where_expression(value))
        else:
            f = (table.c.key == value)
        filters.append(f)
    return filters
