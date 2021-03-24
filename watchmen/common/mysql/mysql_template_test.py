import decimal
import json

from pydantic import BaseModel
from sqlalchemy import *
from sqlalchemy import create_engine, event
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import select
import datetime

Base = declarative_base()


# an example mapping using the base
class TopicSchema(Base):
    __tablename__ = 'topic_schemas'

    topic_id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    type = Column(String)
    description = Column(String)
    _source = Column(JSON)
    create_time = Column(DateTime)
    last_modified = Column(DateTime)


engine = create_engine("mysql+mysqldb://root:123456@localhost:3306/urp",
                       echo=True,
                       future=True,
                       pool_recycle=3600)


def insert_topic_schema():
    topic_schema1 = TopicSchema()
    topic_schema1.topic_id = 5607740540527559761
    topic_schema1.name = "test_distinct_data"
    with open('D:\\test_mysql.json', 'r') as f:
        source = json.load(f)
    topic_schema1._source = source
    topic_schema1.create_time = datetime.date.today()
    session = Session(engine, future=True)
    try:
        session.add(topic_schema1)
    except:
        session.rollback()
        raise
    else:
        session.commit()


class Factor(BaseModel):
    factor_id: decimal.Decimal = 0
    name: str = None
    type: str = None
    description: str = None


def create_topic_table():
    factor_list: list = []

    factor1 = Factor
    factor1.factor_id = 1
    factor1.name = "test1"
    factor1.type = "number"
    factor_list.append(factor1)
    factor2 = Factor
    factor2.factor_id = 2
    factor2.name = "test2"
    factor2.type = "string"
    factor_list.append(factor2)
    factor3 = Factor
    factor3.factor_id = 3
    factor3.name = "test3"
    factor3.type = "date"
    factor_list.append(factor3)

    metadata = MetaData()

    col_list: list = []
    col_kwargs: dict = {}
    for factor in factor_list:
        col_kwargs['name'] = factor.name
        if factor.type == "sequence":
            col_kwargs['type_'] = Integer
            col_kwargs['primary_key'] = True
        elif factor.type == "number":
            col_kwargs['type_'] = Integer
        elif factor.type == "string":
            col_kwargs['type_'] = String
            col_kwargs['nullable'] = True
        elif factor.type == "date":
            col_kwargs['type_'] = Date

        v=Integer
        col1 = Column(name="id", type_=v, primary_key=True)
        col2 = Column("name", String(20), nullable=True)
        col_list.append(col1)
        col_list.append(col2)

    table = Table('test_distinct_data3', metadata)
    for col in col_list:
        table.append_column(col)
    table.create(engine)



def add_column(engine: Engine, table_name: str , columns: list):
    alert_table = 'ALTER TABLE %s \n' % (table_name)
    count = 1
    size = len(columns)
    for column in columns:
        column_name = column.compile(dialect=engine.dialect)
        column_type = column.type.compile(engine.dialect)
        if count == size:
            alert_table = alert_table + ' ADD COLUMN %s %s \n' % (column_name, column_type)
        else:
            alert_table = alert_table + ' ADD COLUMN %s %s, \n' % (column_name, column_type)
            count=count+1
    func = DDL(alert_table)
    session = Session(engine, future=True)
    session.execute(func)



column1 = Column('column5', String(100), primary_key=false)
column2 = Column('column6', String(100), primary_key=false)
new_column_list=[]
new_column_list.append(column1)
new_column_list.append(column2)
add_column(engine, 'test_distinct_data3', new_column_list)
