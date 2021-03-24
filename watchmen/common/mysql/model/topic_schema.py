import json
from datetime import datetime
from operator import eq

import pymongo
from sqlalchemy.engine import reflection

from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, JSON, DateTime, update, DECIMAL, MetaData, Table
from sqlalchemy.orm import declarative_base

from watchmen.common.mysql.mysql_engine import engine
from watchmen.common.storage.collection_list import CollectionList
from watchmen.common.utils.data_utils import convert_to_dict
from watchmen.common.utils.date_utils import DateTimeEncoder

from bson import regex

Base = declarative_base()


class TopicSchema(Base):
    __tablename__ = "topics"

    topicId = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    type = Column(String)
    description = Column(String)
    version = Column(Integer, nullable=False)
    facotrs = Column(JSON)
    createTime = Column(DateTime)
    lastModifyTime = Column(DateTime)

    __mapper_args__ = {
        "version_id_col": version
    }


def create_topic_schema(instance):
    topic_schema = build_topic_schema_model(instance)
    session = Session(engine, future=True)
    try:
        session.add(topic_schema)
    except:
        session.rollback()
        raise
    else:
        session.commit()
        create_topic_table(instance)


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


def update_topic_schema(query_dict, instance):
    topic_schema = build_topic_schema_model(instance)
    session = Session(engine, future=True)
    stmt = update(TopicSchema)

    for key, value in query_dict.items():
        stmt = stmt.where(eq(getattr(TopicSchema, key), value))

    stmt = stmt.values(name=topic_schema.name,
                       description=topic_schema.description,
                       _source=topic_schema._source,
                       createTime=datetime.utcnow(),
                       last_modified=datetime.utcnow()
                       )
    try:
        session.execute(stmt)
        alert_topic_table(session, instance)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


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


def update_topic_schema_of_partial():
    # todo
    pass


def find_one_topic_schema(query_dict):
    session = Session(engine, future=True)
    stmt = select(TopicSchema)
    for key in query_dict.keys():
        value = query_dict[key]
        stmt = stmt.where(eq(getattr(TopicSchema, key), value))
    res = session.execute(stmt).first()
    return json.loads(res[0]._source)


def query_topic_schema_with_pagination(pagination, query_dict, sort_dict):
    result = []
    session = Session(engine, future=True)
    stmt = select(TopicSchema)
    for key in query_dict.keys():
        if isinstance(query_dict.get(key), regex.Regex):
            value = query_dict.get(key)
            pattern = getattr(value, 'pattern')
            if len(pattern) > 0:
                stmt = stmt.where(eq(getattr(TopicSchema, key), pattern))
        else:
            stmt = stmt.where(eq(getattr(TopicSchema, key), pattern))

    if isinstance(sort_dict[0], str):
        order_field = sort_dict[0]
        if sort_dict[1] == pymongo.DESCENDING:
            order_seq = "desc"
        else:
            order_seq = "asc"
        if order_seq == "desc":
            stmt = stmt.order_by(getattr(TopicSchema, order_field).desc())
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
            result.append(json.loads(item._source))
    return result


def build_topic_schema_model(instance):
    instance_dict: dict = convert_to_dict(instance)
    topic_schema = TopicSchema()
    topic_schema.topicId = instance_dict['topicId']
    topic_schema.name = instance_dict['name']
    topic_schema.code = instance_dict.get('code', None)
    topic_schema.description = instance_dict['description']
    topic_schema._source = json.dumps(instance_dict, cls=DateTimeEncoder)
    topic_schema.createTime = datetime.utcnow()
    topic_schema.last_modified = datetime.utcnow()
    return topic_schema
