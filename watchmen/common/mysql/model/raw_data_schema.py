import json
from datetime import datetime
from operator import eq

from sqlalchemy import update
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import declarative_base

from watchmen.common.mysql.mysql_engine import engine
from watchmen.common.storage.collection_list import CollectionList
from watchmen.common.utils.data_utils import convert_to_dict

Base = declarative_base()


class RawSchema(Base):
    __tablename__ = CollectionList.raw_schema

    topic_id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    type = Column(String)
    description = Column(String)
    version = Column(Integer, nullable=False)
    _source = Column(JSON)
    create_time = Column(DateTime)
    last_modified = Column(DateTime)

    __mapper_args__ = {
        "version_id_col": version
    }


def create_raw_topic_schema(instance):
    raw_topic_schema = build_raw_schema_model(instance)
    session = Session(engine, future=True)
    try:
        session.add(raw_topic_schema)
    except:
        session.rollback()
        raise
    else:
        session.commit()


def update_raw_topic_schema(query_dict, instance):
    raw_topic_schema = build_raw_schema_model(instance)
    session = Session(engine, future=True)
    sql_expr = update(raw_topic_schema)

    for key, value in query_dict:
        sql_expr = sql_expr.where(eq(getattr(raw_topic_schema, key), value))

    sql_expr = sql_expr.values(name=raw_topic_schema.name,
                               description=raw_topic_schema.description,
                               _source=raw_topic_schema._source,
                               create_time=datetime.utcnow(),
                               last_modified=datetime.utcnow()
                               )
    session.execute(sql_expr)


def build_raw_schema_model(instance):
    instance_dict: dict = convert_to_dict(instance)
    raw_topic_schema = RawSchema()
    raw_topic_schema.topic_id = instance_dict['topic_id']
    raw_topic_schema.name = instance_dict['name']
    raw_topic_schema.code = instance_dict['code']
    raw_topic_schema.description = instance_dict['description']
    raw_topic_schema._source = json.dumps(instance_dict)
    raw_topic_schema.create_time = datetime.utcnow()
    raw_topic_schema.last_modified = datetime.utcnow()
    return raw_topic_schema
