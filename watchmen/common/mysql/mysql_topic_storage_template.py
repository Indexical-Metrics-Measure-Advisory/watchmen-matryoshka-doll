from sqlalchemy import update, MetaData, DECIMAL, Column, Table, String, and_, or_
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.future import select

from watchmen.common.mysql.mysql_engine import engine
from watchmen.common.utils.data_utils import convert_to_dict


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
