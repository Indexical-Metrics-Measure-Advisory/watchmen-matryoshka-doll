import json

# from sqlalchemy import Table, Column, engine, CLOB, insert

from sqlalchemy import update, Table, and_, or_, delete, Column, DECIMAL, String, CLOB, desc, asc, \
    text, func, DateTime, BigInteger, Date, Integer, engine
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from watchmen.common.data_page import DataPage
from storage.oracle.oracle_engine import dumps
from storage.oracle.oracle_template import capital_to_lower, build_oracle_order, build_oracle_where_expression
from storage.oracle.oracle_utils import parse_obj, count_topic_data_table
from watchmen.common.oracle.table_definition import get_topic_table_by_name, metadata
from storage.snowflake.snowflake import get_surrogate_key
from storage.utils.storage_utils import convert_to_dict, build_data_pages
from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus


def create_raw_pipeline_monitor():
    table = Table('topic_raw_pipeline_monitor', metadata)
    table.append_column(Column(name='id_', type_=String(60), primary_key=True))
    table.append_column(Column(name='data_', type_=CLOB, nullable=True))
    table.append_column(Column(name='sys_inserttime', type_=Date, nullable=True))
    table.append_column(Column(name='sys_updatetime', type_=Date, nullable=True))
    schema = json.loads(PipelineRunStatus.schema_json(indent=1))
    for key, value in schema.get("properties").items():
        column_name = key.lower()
        column_type = value.get("type", None)
        if column_type is None:
            column_format = value.get("format", None)
            if column_format is None:
                table.append_column(Column(name=column_name, type_=CLOB, nullable=True))
            else:
                if column_format == "date-time":
                    table.append_column(Column(name=column_name, type_=Date, nullable=True))
        elif column_type == "boolean":
            table.append_column(Column(name=column_name, type_=String(5), nullable=True))
        elif column_type == "string":
            if column_name == "error":
                table.append_column(Column(name=column_name, type_=CLOB, nullable=True))
            elif column_name == "uid":
                table.append_column(Column(name=column_name.upper(), type_=String(50), quote=True, nullable=True))
            else:
                table.append_column(Column(name=column_name, type_=String(50), nullable=True))
        elif column_type == "integer":
            table.append_column(Column(name=column_name, type_=Integer, nullable=True))
        elif column_type == "array":
            table.append_column(Column(name=column_name, type_=CLOB, nullable=True))
        else:
            raise Exception(column_name + "not support type")
    table.create(engine)


def raw_pipeline_monitor_insert_one(one: object, topic_name: object) -> object:
    table_name = 'topic_' + topic_name
    table = get_topic_table_by_name(table_name)
    one_dict: dict = convert_to_dict(one)
    one_lower_dict = capital_to_lower(one_dict)
    value = {}
    for key in table.c.keys():
        if key == "id_":
            value[key] = get_surrogate_key()
        elif key == "data_":
            value[key] = dumps(one_dict)
        else:
            if isinstance(table.c[key].type, CLOB):
                if one_lower_dict.get(key) is not None:
                    value[key] = dumps(one_lower_dict.get(key))
                else:
                    value[key] = None
            else:
                value[key] = one_lower_dict.get(key)
    stmt = insert(table)
    with engine.connect() as conn:
        conn.execute(stmt, value)


def raw_pipeline_monitor_page_(where, sort, pageable, model, name) -> DataPage:
    count = count_topic_data_table(name)
    table = get_topic_table_by_name(name)
    stmt = select(table).where(build_oracle_where_expression(table, where))
    orders = build_oracle_order(table, sort)
    for order in orders:
        stmt = stmt.order_by(order)
    offset = pageable.pageSize * (pageable.pageNumber - 1)
    # stmt = stmt.offset(offset).limit(pageable.pageSize)
    stmt = text(str(
        stmt.compile(
            compile_kwargs={"literal_binds": True})) + " OFFSET :offset ROWS FETCH NEXT :maxnumrows ROWS ONLY")
    result = []
    with engine.connect() as conn:
        cursor = conn.execute(stmt, {"offset": offset, "maxnumrows": pageable.pageSize}).cursor
        columns = [col[0] for col in cursor.description]
        cursor.rowfactory = lambda *args: dict(zip(columns, args))
        res = cursor.fetchall()
    for row in res:
        if model is not None:
            result.append(parse_obj(model, row, table))
        else:
            result.append(json.loads(row['DATA_']))
    return build_data_pages(pageable, result, count)
