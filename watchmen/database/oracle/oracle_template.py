import datetime
import json
import logging
import operator
from decimal import Decimal
from operator import eq

from sqlalchemy import update, and_, or_, delete, CLOB, desc, asc, \
    text, func, inspect
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from watchmen.common.cache.cache_manage import cacheman, COLUMNS_BY_TABLE_NAME, TOPIC_DICT_BY_NAME
from watchmen.common.data_page import DataPage
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import build_data_pages, convert_to_dict
from watchmen.database.oracle.oracle_engine import dumps
from watchmen.database.oracle.oracle_utils import parse_obj
from watchmen.database.storage.storage_interface import StorageInterface
from watchmen.database.storage.utils.table_utils import get_primary_key

log = logging.getLogger("app." + __name__)

log.info("oracle template initialized")


# @singleton
class OracleStorage(StorageInterface):
    engine = None
    insp = None
    table = None

    def __init__(self, client, table_provider):
        self.engine = client
        self.insp = inspect(client)
        self.table = table_provider

    def build_oracle_where_expression(self, table, where):
        for key, value in where.items():
            if key == "and" or key == "or":
                if isinstance(value, list):
                    filters = []
                    for express in value:
                        result = self.build_oracle_where_expression(table, express)
                        filters.append(result)
                if key == "and":
                    return and_(*filters)
                if key == "or":
                    return or_(*filters)
            else:
                if isinstance(value, dict):
                    for k, v in value.items():
                        if k == "=":
                            return table.c[key.lower()] == v
                        if k == "!=":
                            return operator.ne(table.c[key.lower()], v)
                        if k == "like":
                            if v != "" or v != '' or v is not None:
                                return table.c[key.lower()].like("%" + v + "%")
                        if k == "in":
                            if isinstance(table.c[key.lower()].type, CLOB):
                                if isinstance(v, list):
                                    value_ = ",".join(v)
                                else:
                                    value_ = v
                                return text('json_exists(' + key.lower() + ', \'$?(@ in (\"' + value_ + '\"))\')')
                            else:
                                if isinstance(v, list):
                                    if len(v) != 0:
                                        return table.c[key.lower()].in_(v)
                                elif isinstance(v, str):
                                    v_list = v.split(",")
                                    return table.c[key.lower()].in_(v_list)
                                else:
                                    raise TypeError(
                                        "operator in, the value \"{0}\" is not list or str".format(v))
                        if k == "not-in":
                            if isinstance(table.c[key.lower()].type, CLOB):
                                if isinstance(v, list):
                                    value_ = ",".join(v)
                                else:
                                    value_ = v
                                return text('json_exists(' + key.lower() + ', \'$?(@ not in (\"' + value_ + '\"))\')')
                            else:
                                if isinstance(v, list):
                                    if len(v) != 0:
                                        return table.c[key.lower()].notin_(v)
                                elif isinstance(v, str):
                                    v_list = v.split(",")
                                    return table.c[key.lower()].notin_(v_list)
                                else:
                                    raise TypeError(
                                        "operator not_in, the value \"{0}\" is not list or str".format(v))
                        if k == ">":
                            return table.c[key.lower()] > v
                        if k == ">=":
                            return table.c[key.lower()] >= v
                        if k == "<":
                            return table.c[key.lower()] < v
                        if k == "<=":
                            return table.c[key.lower()] <= v
                        if k == "between":
                            if (isinstance(v, tuple)) and len(v) == 2:
                                return table.c[key.lower()].between(self._check_value_type(v[0]),
                                                                    self._check_value_type(v[1]))
                else:
                    return table.c[key.lower()] == value

    def build_oracle_updates_expression(self, table, updates, stmt_type: str) -> dict:
        if stmt_type == "insert":
            new_updates = {}
            for key in table.c.keys():
                if key == "id_":
                    new_updates[key] = get_surrogate_key()
                elif key == "version_":
                    new_updates[key] = 0
                elif key == "insert_time_" or key == "update_time_":
                    new_updates[key] = datetime.datetime.now().replace(tzinfo=None)
                else:
                    if isinstance(table.c[key].type, CLOB):
                        if updates.get(key) is not None:
                            new_updates[key] = dumps(updates.get(key))
                        else:
                            new_updates[key] = None
                    else:
                        if updates.get(key) is not None:
                            value_ = updates.get(key)
                            if isinstance(value_, dict):
                                for k, v in value_.items():
                                    if k == "_sum":
                                        new_updates[key.lower()] = v
                                    elif k == "_count":
                                        new_updates[key.lower()] = v
                                    elif k == "_avg":
                                        new_updates[key.lower()] = v
                            else:
                                new_updates[key] = value_
                        else:
                            default_value = self._get_table_column_default_value(table.name, key)
                            if default_value is not None:
                                value_ = default_value.strip("'").strip(" ")
                                if value_.isdigit():
                                    new_updates[key] = Decimal(value_)
                                else:
                                    new_updates[key] = value_
                            else:
                                new_updates[key] = None
            return new_updates
        elif stmt_type == "update":
            new_updates = {}
            for key in table.c.keys():
                if key == "version_":
                    new_updates[key] = updates.get(key) + 1
                elif key == "update_time_":
                    new_updates[key] = datetime.datetime.now().replace(tzinfo=None)
                else:
                    if isinstance(table.c[key].type, CLOB):
                        if updates.get(key) is not None:
                            new_updates[key] = dumps(updates.get(key))
                    else:
                        if updates.get(key) is not None:
                            value_ = updates.get(key)
                            if isinstance(value_, dict):
                                for k, v in value_.items():
                                    if k == "_sum":
                                        new_updates[key.lower()] = text(f'{key.lower()} + {v}')
                                    elif k == "_count":
                                        new_updates[key.lower()] = text(f'{key.lower()} + {v}')
                                    elif k == "_avg":
                                        pass  # todo
                            else:
                                new_updates[key] = value_
            return new_updates

    def build_oracle_order(self, table, order_: list):
        result = []
        if order_ is None:
            return result
        else:
            for item in order_:
                if isinstance(item, tuple):
                    if item[1] == "desc":
                        new_ = desc(table.c[item[0].lower()])
                        result.append(new_)
                    if item[1] == "asc":
                        new_ = asc(table.c[item[0].lower()])
                        result.append(new_)
            return result

    def insert_one(self, one, model, name):
        table = self.table.get_table_by_name(name)
        one_dict: dict = convert_to_dict(one)
        values = {}
        for key, value in one_dict.items():
            if isinstance(table.c[key.lower()].type, CLOB):
                if value is not None:
                    values[key.lower()] = dumps(value)
                else:
                    values[key.lower()] = None
            else:
                values[key.lower()] = value
        stmt = insert(table).values(values)
        with self.engine.connect() as conn:
            conn.execute(stmt)
        return model.parse_obj(one)

    def insert_all(self, data, model, name):
        table = self.table.get_table_by_name(name)
        stmt = insert(table)
        value_list = []
        for item in data:
            instance_dict: dict = convert_to_dict(item)
            values = {}
            for key in table.c.keys():
                values[key] = instance_dict.get(key)
            value_list.append(values)
        with self.engine.connect() as conn:
            conn.execute(stmt, value_list)

    def update_one(self, one, model, name) -> any:
        table = self.table.get_table_by_name(name)
        stmt = update(table)
        one_dict: dict = convert_to_dict(one)
        primary_key = get_primary_key(name)
        stmt = stmt.where(
            eq(table.c[primary_key.lower()], one_dict.get(primary_key)))
        values = {}
        for key, value in one_dict.items():
            if isinstance(table.c[key.lower()].type, CLOB):
                if value is not None:
                    values[key.lower()] = dumps(value)
                else:
                    values[key.lower()] = None
            else:
                values[key.lower()] = value
        stmt = stmt.values(values)
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt)
        return model.parse_obj(one)

    def update_one_first(self, where, updates, model, name):
        table = self.table.get_table_by_name(name)
        stmt = update(table)
        stmt = stmt.where(self.build_oracle_where_expression(table, where))
        stmt = stmt.where(text("ROWNUM=1"))
        instance_dict: dict = convert_to_dict(updates)
        values = {}
        for key, value in instance_dict.items():
            if isinstance(table.c[key.lower()].type, CLOB):
                if value is not None:
                    values[key.lower()] = dumps(value)
                else:
                    values[key.lower()] = None
            else:
                values[key.lower()] = value
        stmt = stmt.values(values)
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt)
        return model.parse_obj(updates)

    def update_(self, where, updates, model, name):
        table = self.table.get_table_by_name(name)
        stmt = update(table)
        stmt = stmt.where(self.build_oracle_where_expression(table, where))
        instance_dict: dict = convert_to_dict(updates)
        values = {}
        for key, value in instance_dict.items():
            if key != get_primary_key(name):
                values[key] = value
        stmt = stmt.values(values)
        session = Session(self.engine, future=True)
        try:
            session.execute(stmt)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def pull_update(self, where, updates, model, name):
        results = self.find_(where, model, name)
        updates_dict = convert_to_dict(updates)
        for key, value in updates_dict.items():
            for res in results:
                if isinstance(getattr(res, key), list):
                    setattr(res, key, getattr(res, key).remove(value["in"][0]))
                    self.update_one(res, model, name)
        # can't use update_, because the where have the json filed query
        # update_(where, results, model, name)

    def delete_by_id(self, id_, name):
        table = self.table.get_table_by_name(name)
        key = get_primary_key(name)
        stmt = delete(table).where(eq(table.c[key.lower()], id_))
        with self.engine.connect() as conn:
            conn.execute(stmt)
            # conn.commit()

    def delete_one(self, where: dict, name: str):
        table = self.table.get_table_by_name(name)
        stmt = delete(table).where(self.build_oracle_where_expression(table, where))
        with self.engine.connect() as conn:
            conn.execute(stmt)

    def delete_(self, where, model, name):
        table = self.table.get_table_by_name(name)
        if where is None:
            stmt = delete(table)
        else:
            stmt = delete(table).where(self.build_oracle_where_expression(table, where))
        with self.engine.connect() as conn:
            conn.execute(stmt)

    def find_by_id(self, id_, model, name):
        table = self.table.get_table_by_name(name)
        primary_key = get_primary_key(name)
        stmt = select(table).where(eq(table.c[primary_key.lower()], id_))
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            result = cursor.fetchone()
        if result is None:
            return
        else:
            return parse_obj(model, result, table)

    def find_one(self, where, model, name):
        table = self.table.get_table_by_name(name)
        stmt = select(table)
        stmt = stmt.where(self.build_oracle_where_expression(table, where))
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            result = cursor.fetchone()
        if result is None:
            return
        else:
            return parse_obj(model, result, table)

    def find_(self, where: dict, model, name: str) -> list:
        table = self.table.get_table_by_name(name)
        stmt = select(table)
        where_expression = self.build_oracle_where_expression(table, where)
        if where_expression is not None:
            stmt = stmt.where(where_expression)
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            result = cursor.fetchall()
        if result is not None:
            return [parse_obj(model, row, table) for row in result]
        else:
            return None

    def list_all(self, model, name):
        table = self.table.get_table_by_name(name)
        stmt = select(table)
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            res = cursor.fetchall()
        result = []
        for row in res:
            result.append(parse_obj(model, row, table))
        return result

    def list_(self, where, model, name) -> list:
        table = self.table.get_table_by_name(name)
        stmt = select(table).where(self.build_oracle_where_expression(table, where))
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            res = cursor.fetchall()
        result = []
        for row in res:
            result.append(parse_obj(model, row, table))
        return result

    def page_all(self, sort, pageable, model, name) -> DataPage:
        count = self.count_table(name)
        table = self.table.get_table_by_name(name)
        stmt = select(table)
        orders = self.build_oracle_order(table, sort)
        for order in orders:
            stmt = stmt.order_by(order)
        offset = pageable.pageSize * (pageable.pageNumber - 1)
        stmt = text(str(
            stmt.compile(
                compile_kwargs={"literal_binds": True})) + " OFFSET :offset ROWS FETCH NEXT :maxnumrows ROWS ONLY")
        result = []
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt, {"offset": offset, "maxnumrows": pageable.pageSize}).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            res = cursor.fetchall()
        for row in res:
            result.append(parse_obj(model, row, table))
        return build_data_pages(pageable, result, count)

    def page_(self, where, sort, pageable, model, name) -> DataPage:
        count = self.count_table(name)
        table = self.table.get_table_by_name(name)
        stmt = select(table).where(self.build_oracle_where_expression(table, where))
        orders = self.build_oracle_order(table, sort)
        for order in orders:
            stmt = stmt.order_by(order)
        offset = pageable.pageSize * (pageable.pageNumber - 1)
        stmt = text(str(
            stmt.compile(
                compile_kwargs={"literal_binds": True})) + " OFFSET :offset ROWS FETCH NEXT :maxnumrows ROWS ONLY")
        result = []
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt, {"offset": offset, "maxnumrows": pageable.pageSize}).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            res = cursor.fetchall()
        for row in res:
            result.append(parse_obj(model, row, table))
        return build_data_pages(pageable, result, count)

    def clear_metadata(self):
        self.table.metadata.clear()

    '''
    protected method, used by class own method
    '''

    def _get_table_column_default_value(self, table_name, column_name):
        cached_columns = cacheman[COLUMNS_BY_TABLE_NAME].get(table_name)
        if cached_columns is not None:
            columns = cached_columns
        else:
            columns = self.insp.get_columns(table_name)
            cacheman[COLUMNS_BY_TABLE_NAME].set(table_name, columns)
        for column in columns:
            if column["name"] == column_name:
                return column["default"]

    def _convert_dict_key(self, dict_info, topic_name):
        if dict_info is None:
            return None
        new_dict = {}
        factors = self.get_topic_factors(topic_name)
        for factor in factors:
            new_dict[factor['name']] = dict_info[factor['name'].upper()]
        new_dict['id_'] = dict_info['ID_']
        if 'TENANT_ID_' in dict_info:
            new_dict['tenant_id_'] = dict_info.get("TENANT_ID_", 1)
        if "INSERT_TIME_" in dict_info:
            new_dict['insert_time_'] = dict_info.get("INSERT_TIME_", datetime.datetime.now().replace(tzinfo=None))
        if "UPDATE_TIME_" in dict_info:
            new_dict['update_time_'] = dict_info.get("UPDATE_TIME_", datetime.datetime.now().replace(tzinfo=None))
        if "VERSION_" in dict_info:
            new_dict['version_'] = dict_info.get("VERSION_", 0)
        if "AGGREGATE_ASSIST_" in dict_info:
            new_dict['aggregate_assist_'] = dict_info.get("AGGREGATE_ASSIST_")
        return new_dict

    def _convert_list_elements_key(self, list_info, topic_name):
        if list_info is None:
            return None
        new_dict = {}
        new_list = []
        factors = self._get_topic_factors(topic_name)
        for item in list_info:
            for factor in factors:
                new_dict[factor['name']] = item[factor['name'].upper()]
                new_dict['id_'] = item['ID_']
                if 'TENANT_ID_' in item:
                    new_dict['tenant_id_'] = item.get("TENANT_ID_", 1)
                if "INSERT_TIME_":
                    new_dict['insert_time_'] = item.get("INSERT_TIME_", datetime.datetime.now().replace(tzinfo=None))
                if "UPDATE_TIME_":
                    new_dict['update_time_'] = item.get("UPDATE_TIME_", datetime.datetime.now().replace(tzinfo=None))
                if "VERSION_" in item:
                    new_dict['version_'] = item.get("VERSION_", 0)
                if "AGGREGATE_ASSIST_" in item:
                    new_dict['aggregate_assist_'] = item.get("AGGREGATE_ASSIST_")
                new_list.append(new_dict)
        return new_list

    @staticmethod
    def _check_value_type(value):
        if isinstance(value, datetime.datetime):
            return func.to_date(value, "yyyy-mm-dd hh24:mi:ss")
        elif isinstance(value, datetime.date):
            return func.to_date(value, "yyyy-mm-dd")
        else:
            return value

    def count_table(self, table_name):
        primary_key = get_primary_key(table_name)
        stmt = 'SELECT count(%s) AS count FROM %s' % (primary_key, table_name)
        with self.engine.connect() as conn:
            cursor = conn.execute(text(stmt)).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            result = cursor.fetchone()
        return result['COUNT']

    def count_topic_data_table(self, table_name):
        stmt = 'SELECT count(%s) AS count FROM %s' % ('id_', table_name)
        with self.engine.connect() as conn:
            cursor = conn.execute(text(stmt)).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            result = cursor.fetchone()
        return result['COUNT']

    def check_topic_type(self, topic_name):
        topic = self._get_topic(topic_name)
        return topic['TYPE']

    def get_topic_factors(self, topic_name):
        topic = self._get_topic(topic_name)
        factors = json.loads(topic['FACTORS'])
        return factors

    def _get_topic(self, topic_name) -> any:
        if cacheman[TOPIC_DICT_BY_NAME].get(topic_name) is not None:
            return cacheman[TOPIC_DICT_BY_NAME].get(topic_name)
        table = self.table.get_table_by_name("topics")
        select_stmt = select(table).where(
            self.build_oracle_where_expression(table, {"name": topic_name}))
        with self.engine.connect() as conn:
            cursor = conn.execute(select_stmt).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            result = cursor.fetchone()
            if result is None:
                raise
            else:
                cacheman[TOPIC_DICT_BY_NAME].set(topic_name, result)
                return result
