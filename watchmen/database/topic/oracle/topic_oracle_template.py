import datetime
import json
import logging
import operator
from decimal import Decimal
from operator import eq

from sqlalchemy import update, and_, or_, delete, CLOB, desc, asc, \
    text, func, inspect, Table, MetaData
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import NoSuchTableError, IntegrityError
from sqlalchemy.future import select

from watchmen.common.cache.cache_manage import cacheman, COLUMNS_BY_TABLE_NAME
from watchmen.common.data_page import DataPage
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import build_data_pages, build_collection_name, convert_to_dict, capital_to_lower
from watchmen.database.find_storage_template import find_storage_template
from storage.oracle.oracle_engine import dumps
from storage.oracle.oracle_utils import parse_obj
from storage.storage.exception.exception import InsertConflictError, OptimisticLockError
from watchmen.database.topic.topic_storage_interface import TopicStorageInterface

log = logging.getLogger("app." + __name__)



storage_template = find_storage_template()


class OracleTopicStorage(TopicStorageInterface):
    engine = None
    insp = None
    metadata = MetaData()

    def __init__(self, client):
        self.engine = client
        self.insp = inspect(client)
        log.info("topic oracle template initialized")

    def get_topic_table_by_name(self, table_name):
        table = Table(table_name, self.metadata, extend_existing=False, autoload=True, autoload_with=self.engine)
        return table

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

    '''
    topic data interface
    '''

    def drop_(self, topic_name):
        return self.drop_topic_data_table(topic_name)

    def drop_topic_data_table(self, topic_name):
        try:
            table_name = build_collection_name(topic_name)
            table = self.get_topic_table_by_name(table_name)
            table.drop(self.engine)
            self.clear_metadata()
        except NoSuchTableError as err:
            log.info("NoSuchTableError: {0}".format(table_name))

    def topic_data_delete_(self, where, topic_name):
        table_name = build_collection_name(topic_name)
        table = self.get_topic_table_by_name(table_name)
        if where is None:
            stmt = delete(table)
        else:
            stmt = delete(table).where(self.build_oracle_where_expression(table, where))
        with self.engine.connect() as conn:
            conn.execute(stmt)

    def topic_data_insert_one(self, one, topic_name):
        table_name = build_collection_name(topic_name)
        table = self.get_topic_table_by_name(table_name)
        one_dict: dict = capital_to_lower(convert_to_dict(one))
        value = self.build_oracle_updates_expression(table, one_dict, "insert")
        stmt = insert(table)
        with self.engine.connect() as conn:
            with conn.begin():
                try:
                    result = conn.execute(stmt, value)
                except IntegrityError as e:
                    raise InsertConflictError("InsertConflict")
        return result.rowcount

    def topic_data_insert_(self, data, topic_name):
        table_name = build_collection_name(topic_name)
        table = self.get_topic_table_by_name(table_name)
        values = []
        for instance in data:
            one_dict: dict = capital_to_lower(convert_to_dict(instance))
            value = self.build_oracle_updates_expression(table, one_dict, "insert")
            values.append(value)
        stmt = insert(table)
        with self.engine.connect() as conn:
            result = conn.execute(stmt, values)

    def topic_data_update_one(self, id_: str, one: any, topic_name: str):
        table_name = build_collection_name(topic_name)
        table = self.get_topic_table_by_name(table_name)
        stmt = update(table).where(eq(table.c['id_'], id_))
        one_dict = capital_to_lower(convert_to_dict(one))
        value = self.build_oracle_updates_expression(table, one_dict, "update")
        stmt = stmt.values(value)
        with self.engine.begin() as conn:
            result = conn.execute(stmt)
        return result.rowcount

    def topic_data_update_one_with_version(self, id_: str, version_: int, one: any, topic_name: str):
        table_name = build_collection_name(topic_name)
        table = self.get_topic_table_by_name(table_name)
        stmt = update(table).where(and_(eq(table.c['id_'], id_), eq(table.c['version_'], version_)))
        one_dict = capital_to_lower(convert_to_dict(one))
        value = self.build_oracle_updates_expression(table, one_dict, "update")
        stmt = stmt.values(value)
        with self.engine.begin() as conn:
            result = conn.execute(stmt)
        if result.rowcount == 0:
            raise OptimisticLockError("Optimistic lock error")

    def topic_data_update_(self, query_dict, instances: list, topic_name):
        table_name = build_collection_name(topic_name)
        table = self.get_topic_table_by_name(table_name)
        stmt = (update(table).
                where(self.build_oracle_where_expression(table, query_dict)))
        values = []
        for instance in instances:
            one_dict = capital_to_lower(convert_to_dict(instance))
            value = self.build_oracle_updates_expression(table, one_dict)
            values.append(value)
        stmt = stmt.values(values)
        with self.engine.begin() as conn:
            result = conn.execute(stmt)

    def topic_data_find_by_id(self, id_: str, topic_name: str) -> any:
        return self.topic_data_find_one({"id_": id_}, topic_name)

    def topic_data_find_one(self, where, topic_name) -> any:
        table_name = build_collection_name(topic_name)
        table = self.get_topic_table_by_name(table_name)
        stmt = select(table).where(self.build_oracle_where_expression(table, where))
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            row = cursor.fetchone()
        if row is None:
            return None
        else:
            result = {}
            for index, name in enumerate(columns):
                if isinstance(table.c[name.lower()].type, CLOB):
                    if row[name] is not None:
                        result[name] = json.loads(row[name])
                    else:
                        result[name] = None
                else:
                    result[name] = row[name]
            return self._convert_dict_key(result, topic_name)

    def topic_data_find_(self, where, topic_name):
        table_name = build_collection_name(topic_name)
        table = self.get_topic_table_by_name(table_name)
        stmt = select(table).where(self.build_oracle_where_expression(table, where))
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            rows = cursor.fetchall()
        if rows is None:
            return None
        else:
            if isinstance(rows, list):
                results = []
                for row in rows:
                    result = {}
                    for index, name in enumerate(columns):
                        if isinstance(table.c[name.lower()].type, CLOB):
                            if row[name] is not None:
                                result[name] = json.loads(row[name])
                            else:
                                result[name] = None
                        else:
                            result[name] = row[name]
                    results.append(self._convert_dict_key(result, topic_name))
                return results
            else:
                result = {}
                for index, name in enumerate(columns):
                    if isinstance(table.c[name.lower()].type, CLOB):
                        result[name] = dumps(rows[index])
                    else:
                        result[name] = rows[index]
                return result

    def topic_data_find_with_aggregate(self, where, topic_name, aggregate):
        table_name = 'topic_' + topic_name
        table = self.get_topic_table_by_name(table_name)
        return_column_name = None
        for key, value in aggregate.items():
            if value == "sum":
                stmt = select(text(f'sum({key.lower()}) as sum_{key.lower()}'))
                return_column_name = f'SUM_{key.upper()}'
            elif value == "count":
                stmt = select(f'count(*) as count')
                return_column_name = 'COUNT'
            elif value == "avg":
                stmt = select(text(f'avg({key.lower()}) as avg_{key.lower()}'))
                return_column_name = f'AVG_{key.upper()}'
        stmt = stmt.select_from(table)
        stmt = stmt.where(self.build_oracle_where_expression(table, where))
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            res = cursor.fetchone()
        if res is None:
            return None
        else:
            return res[return_column_name]

    def topic_data_list_all(self, topic_name) -> list:
        table_name = build_collection_name(topic_name)
        table = self.get_topic_table_by_name(table_name)
        stmt = select(table)
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            rows = cursor.fetchall()

            if rows is None:
                return None
            else:
                results = []
                for row in rows:
                    result = {}
                    for index, name in enumerate(columns):
                        if isinstance(table.c[name.lower()].type, CLOB):
                            if row[name] is not None:
                                result[name] = json.loads(row[name])
                            else:
                                result[name] = None
                        else:
                            result[name] = row[name]
                    if storage_template.check_topic_type(name) == "raw":
                        results.append(result['DATA_'])
                    else:
                        results.append(result)
                if storage_template.check_topic_type(name) == "raw":
                    return results
                else:
                    return self._convert_list_elements_key(results, topic_name)

    def topic_data_page_(self, where, sort, pageable, model, name) -> DataPage:
        table_name = build_collection_name(name)
        count = self.count_topic_data_table(table_name)
        table = self.get_topic_table_by_name(table_name)
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
        if storage_template.check_topic_type(name) == "raw":
            for row in res:
                result.append(json.loads(row['DATA_']))
        else:
            for row in res:
                if model is not None:
                    result.append(parse_obj(model, row, table))
                else:
                    result.append(row)
        return build_data_pages(pageable, result, count)

    def clear_metadata(self):
        self.metadata.clear()

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
        factors = storage_template.get_topic_factors(topic_name)
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
        factors = storage_template.get_topic_factors(topic_name)
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

    def count_topic_data_table(self, table_name):
        stmt = 'SELECT count(%s) AS count FROM %s' % ('id_', table_name)
        with self.engine.connect() as conn:
            cursor = conn.execute(text(stmt)).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            result = cursor.fetchone()
        return result['COUNT']
