import logging
from operator import eq

import pymongo
from bson import regex
from sqlalchemy import update, MetaData, DECIMAL, Column, Table, String, insert, and_, or_
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from watchmen.common.mysql.model.table_definition import get_table_model, get_primary_key, parse_obj, count_table
from watchmen.common.mysql.mysql_engine import engine
from watchmen.common.utils.data_utils import build_data_pages
from watchmen.common.utils.data_utils import convert_to_dict

log = logging.getLogger("app." + __name__)  

log.info("mysql template initialized")


def create(collection_name, instance, base_model):
    table_instance = get_table_model(collection_name)()
    instance_dict: dict = convert_to_dict(instance)
    for key, value in instance_dict.items():
        setattr(table_instance, key, value)
    session = Session(engine, future=True)
    try:
        session.add(table_instance)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
    return base_model.parse_obj(instance)


def update_one(collection_name, query_dict, instance, base_model):
    table = get_table_model(collection_name)
    session = Session(engine, future=True)
    stmt = update(table)

    for key, value in query_dict.items():
        stmt = stmt.where(eq(getattr(table, key), value))

    instance_dict: dict = convert_to_dict(instance)

    values = {}
    for key, value in instance_dict.items():
        if key != get_primary_key(collection_name):
            values[key] = value

    stmt = stmt.values(values)
    try:
        session.execute(stmt)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

    return base_model.parse_obj(instance)


def find_one(collection_name, query_dict, base_model):
    table = get_table_model(collection_name)
    stmt = select(table)
    for key in query_dict.keys():
        value = query_dict[key]
        stmt = stmt.where(eq(getattr(table, key), value))
    session = Session(engine, future=True)
    res = session.execute(stmt).first()
    return parse_obj(base_model, res[0])


def query_with_pagination(collection_name, pagination, base_model, query_dict=None, sort_dict=None):
    count = count_table(collection_name)
    table = get_table_model(collection_name)
    result = []
    session = Session(engine, future=True)
    stmt = select(table)
    for key in query_dict.keys():
        if isinstance(query_dict.get(key), regex.Regex):
            value = query_dict.get(key)
            pattern = getattr(value, 'pattern')
            if len(pattern) > 0:
                stmt = stmt.where(eq(getattr(table, key), pattern))
        else:
            stmt = stmt.where(eq(getattr(table, key), pattern))

    if isinstance(sort_dict[0], str):
        order_field = sort_dict[0]
        if sort_dict[1] == pymongo.DESCENDING:
            order_seq = "desc"
        else:
            order_seq = "asc"
        if order_seq == "desc":
            stmt = stmt.order_by(getattr(table, order_field).desc())
    else:
        for tup in sort_dict:
            order_field = tup[0]
            if tup[1] == pymongo.DESCENDING:
                order_seq = "desc"
            if tup[1] == pymongo.ASCENDING:
                order_seq = "asc"
            if order_seq == "desc":
                stmt = stmt.order_by(order_field.desc())

    offset = pagination.pageSize * (pagination.pageNumber - 1)
    stmt = stmt.offset(offset).limit(pagination.pageSize)
    res = session.execute(stmt)
    for row in res:
        for item in row:
            result.append(parse_obj(base_model, item))
    return build_data_pages(pagination, result, count)


def create_topic_table(instance):
    metadata = MetaData()
    instance_dict: dict = convert_to_dict(instance)
    topic_name = instance_dict.get('name')
    factors = instance_dict.get('factors')
    table = Table('topic_' + topic_name, metadata)
    key = Column(name="id", type_=DECIMAL(50), primary_key=True)
    table.append_column(key)
    for factor in factors:
        col = Column(name=factor.get('name'), type_=String(20), nullable=True)
        table.append_column(col)
    table.create(engine)


def alert_topic_table(session, instance):
    metadata = MetaData()
    instance_dict: dict = convert_to_dict(instance)
    topic_name = instance_dict.get('name')
    table_name = 'topic_' + topic_name
    table = Table('topic_' + topic_name, metadata, autoload=True, autoload_with=engine)
    factors = instance_dict.get('factors')
    existed_cols = []
    for col in table.columns:
        existed_cols.append(col.name)
    for factor in factors:
        if factor.get('name') in existed_cols:
            continue
        else:
            column = Column(factor.get('name'), String(20))
            add_column(session, table_name, column)


def add_column(session, table_name, column):
    column_name = column.compile(dialect=engine.dialect)
    column_type = column.type.compile(engine.dialect)
    session.execute('ALTER TABLE %s ADD COLUMN %s %s' % (table_name, column_name, column_type))


def insert_topic_instances(topic_name, instances):
    metadata = MetaData()
    table = Table('topic_' + topic_name, metadata, autoload=True, autoload_with=engine)
    values = []
    for instance in instances:
        instance_dict: dict = convert_to_dict(instance)
        value = {}
        for key in table.c.keys():
            value[key] = instance_dict.get(key)
        values.append(value)
    stmt = insert(table)
    with engine.connect() as conn:
        result = conn.execute(stmt, values)
        conn.commit()


def insert_topic_instance(topic_name, instance):
    return insert_topic_instances(topic_name, [instance])


def update_topic_instance(topic_name, query_dict, instance):
    metadata = MetaData()
    table = Table('topic_' + topic_name, metadata, autoload=True, autoload_with=engine)
    stmt = (update(table).
            where(*build_where_expression(table, query_dict)))
    instance_dict: dict = convert_to_dict(instance)
    values = {}
    for key, value in instance_dict.items():
        if key != 'id':
            values[key] = value
    stmt = stmt.values(values)
    with engine.begin() as conn:
        conn.execute(stmt)


def query_topic_instance(topic_name, conditions):
    metadata = MetaData()
    table = Table('topic_' + topic_name, metadata, autoload=True, autoload_with=engine)
    stmt = select(table).where(*build_where_expression(table, conditions))
    with engine.connect() as conn:
        result = conn.execute(stmt)
        conn.commit()
        return result


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
