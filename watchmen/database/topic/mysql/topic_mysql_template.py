import json
import logging
import operator
from datetime import datetime
from decimal import Decimal
from operator import eq

from sqlalchemy import Table, MetaData
from sqlalchemy import update, and_, or_, delete, desc, asc, \
    text, JSON, inspect, func
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.exc import NoSuchTableError, IntegrityError
from sqlalchemy.future import select

from watchmen.common.cache.cache_manage import cacheman, STMT, COLUMNS_BY_TABLE_NAME
from watchmen.common.data_page import DataPage
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import build_data_pages, capital_to_lower, build_collection_name
from watchmen.common.utils.data_utils import convert_to_dict
from watchmen.database.mysql.mysql_utils import parse_obj
from watchmen.database.storage import storage_template
from watchmen.database.storage.exception.exception import OptimisticLockError, InsertConflictError
from watchmen.database.topic.topic_storage_interface import TopicStorageInterface

log = logging.getLogger("app." + __name__)




# @singleton
class MysqlTopicStorage(TopicStorageInterface):
    metadata = MetaData()
    engine = None
    insp = None

    def __init__(self, client):
        self.engine = client
        self.insp = inspect(client)
        log.info("mysql template initialized")

    def get_topic_table_by_name(self, table_name):
        table = Table(table_name, self.metadata, extend_existing=False, autoload=True, autoload_with=self.engine)
        return table

    def build_mysql_where_expression(self, table, where):
        for key, value in where.items():
            if key == "and" or key == "or":
                result_filters = self.get_result_filters(table, value)
                if key == "and":
                    return and_(*result_filters)
                if key == "or":
                    return or_(*result_filters)
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
                            if isinstance(table.c[key.lower()].type, JSON):
                                stmt = ""
                                if isinstance(v, list):
                                    # value_ = ",".join(v)
                                    for item in v:
                                        if stmt == "":
                                            stmt = "JSON_CONTAINS(" + key.lower() + ", '[\"" + item + "\"]', '$') = 1"
                                        else:
                                            stmt = stmt + " or JSON_CONTAINS(" + key.lower() + ", '[\"" + item + "\"]', '$') = 1 "
                                else:
                                    value_ = v
                                    stmt = "JSON_CONTAINS(" + key.lower() + ", '[\"" + value_ + "\"]', '$') = 1"
                                return text(stmt)
                            else:
                                if isinstance(v, list):
                                    return table.c[key.lower()].in_(v)
                                elif isinstance(v, str):
                                    v_list = v.split(",")
                                    return table.c[key.lower()].in_(v_list)
                                else:
                                    raise TypeError(
                                        "operator in, the value \"{0}\" is not list or str".format(v))
                        if k == "not-in":
                            if isinstance(table.c[key.lower()].type, JSON):
                                if isinstance(v, list):
                                    value_ = ",".join(v)
                                else:
                                    value_ = v
                                stmt = "JSON_CONTAINS(" + key.lower() + ", '[\"" + value_ + "\"]', '$') = 0"
                                return text(stmt)
                            else:
                                if isinstance(v, list):
                                    return table.c[key.lower()].notin_(v)
                                elif isinstance(v, str):
                                    v_list = ",".join(v)
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
                                return table.c[key.lower()].between(v[0],
                                                                    v[1])
                else:
                    return table.c[key.lower()] == value

    def get_result_filters(self, table, value):
        if isinstance(value, list):
            result_filters = []
            for express in value:
                result = self.build_mysql_where_expression(table, express)
                result_filters.append(result)
            return result_filters
        else:
            return []

    # @staticmethod
    def build_mysql_updates_expression(self,table, updates, stmt_type: str) -> dict:
        if stmt_type == "insert":
            new_updates = {}
            for key in table.c.keys():
                if key == "id_":
                    new_updates[key] = get_surrogate_key()
                elif key == "version_":
                    new_updates[key] = 0
                else:
                    if isinstance(table.c[key].type, JSON):
                        if updates.get(key) is not None:
                            new_updates[key] = updates.get(key)
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
                                        pass  # todo
                            else:
                                new_updates[key] = value_
                        else:
                            default_value = self.get_table_column_default_value(table.name, key)
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
                    if isinstance(table.c[key].type, JSON):
                        if updates.get(key) is not None:
                            new_updates[key] = updates.get(key)
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

    @staticmethod
    def build_mysql_order(table, order_: list):
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

    def clear_metadata(self):
        self.metadata.clear()

    '''
    topic data interface
    '''

    def drop_(self, topic_name):
        return self.drop_topic_data_table(topic_name)

    def drop_topic_data_table(self, topic_name):
        table_name = 'topic_' + topic_name
        try:
            table = self.get_topic_table_by_name(table_name)
            table.drop(self.engine)
        except NoSuchTableError:
            log.warning("drop table \"{0}\" not existed".format(table_name))

    def topic_data_delete_(self, where, topic_name):
        table_name = 'topic_' + topic_name
        table = self.get_topic_table_by_name(table_name)
        if where is None:
            stmt = delete(table)
        else:
            stmt = delete(table).where(self.build_mysql_where_expression(table, where))
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt)

    @staticmethod
    def build_stmt(stmt_type, table_name, table):
        key = stmt_type + "-" + table_name
        result = cacheman[STMT].get(key)
        if result is not None:
            return result
        else:
            if stmt_type == "insert":
                stmt = insert(table)
                cacheman[STMT].set(key, stmt)
                return stmt
            elif stmt_type == "update":
                stmt = update(table)
                cacheman[STMT].set(key, stmt)
                return stmt
            elif stmt_type == "select":
                stmt = select(table)
                cacheman[STMT].set(key, stmt)
                return stmt

    def topic_data_insert_one(self, one, topic_name):
        table_name = 'topic_' + topic_name
        table = self.get_topic_table_by_name(table_name)
        stmt = self.build_stmt("insert", table_name, table)
        one_dict: dict = capital_to_lower(convert_to_dict(one))
        value = self.build_mysql_updates_expression(table, one_dict, "insert")
        with self.engine.connect() as conn:
            with conn.begin():
                try:
                    result = conn.execute(stmt, value)
                except IntegrityError as e:
                    raise InsertConflictError("InsertConflict")
        return result.rowcount

    def topic_data_insert_(self, data, topic_name):
        table_name = 'topic_' + topic_name
        table = self.get_topic_table_by_name(table_name)
        values = []
        for instance in data:
            instance_dict: dict = convert_to_dict(instance)
            instance_dict['id_'] = get_surrogate_key()
            value = {}
            for key in table.c.keys():
                value[key] = instance_dict.get(key)
            values.append(value)
        stmt = self.build_stmt("insert", table_name, table)
        with self.engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt, values)

    def topic_data_update_one(self, id_: str, one: any, topic_name: str):
        table_name = 'topic_' + topic_name
        table = self.get_topic_table_by_name(table_name)
        stmt = self.build_stmt("update", table_name, table)

        stmt = stmt.where(eq(table.c['id_'], id_))
        one_dict = convert_to_dict(one)
        values = self.build_mysql_updates_expression(table, capital_to_lower(one_dict), "update")
        stmt = stmt.values(values)
        with self.engine.begin() as conn:
            conn.execute(stmt)

    def topic_data_update_one_with_version(self, id_: str, version_: int, one: any, topic_name: str):
        table_name = 'topic_' + topic_name
        table = self.get_topic_table_by_name(table_name)
        stmt = self.build_stmt("update", table_name, table)
        stmt = stmt.where(and_(eq(table.c['id_'], id_), eq(table.c['version_'], version_)))
        one_dict = convert_to_dict(one)
        one_dict['version_'] = version_
        values = self.build_mysql_updates_expression(table, capital_to_lower(one_dict), "update")
        stmt = stmt.values(values)
        with self.engine.begin() as conn:
            result = conn.execute(stmt)
        if result.rowcount == 0:
            raise OptimisticLockError("Optimistic lock error")

    def topic_data_update_(self, query_dict, instance, topic_name):
        table_name = 'topic_' + topic_name
        table = self.get_topic_table_by_name(table_name)
        stmt = self.build_stmt("update", table_name, table)
        stmt = (stmt.
                where(self.build_mysql_where_expression(table, query_dict)))
        instance_dict: dict = convert_to_dict(instance)
        values = {}
        for key, value in instance_dict.items():
            if key != 'id_':
                if key.lower() in table.c.keys():
                    values[key.lower()] = value
        stmt = stmt.values(values)
        with self.engine.begin() as conn:
            # with conn.begin():
            conn.execute(stmt)

    def topic_data_find_by_id(self, id_: str, topic_name: str) -> any:
        return self.topic_data_find_one({"id_": id_}, topic_name)

    def topic_data_find_one(self, where, topic_name) -> any:
        table_name = 'topic_' + topic_name
        table = self.get_topic_table_by_name(table_name)
        stmt = self.build_stmt("select", table_name, table)
        stmt = stmt.where(self.build_mysql_where_expression(table, where))
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
        if row is None:
            return None
        else:
            result = {}
            for index, name in enumerate(columns):
                if isinstance(table.c[name.lower()].type, JSON):
                    if row[index] is not None:
                        result[name] = json.loads(row[index])
                    else:
                        result[name] = None
                else:
                    result[name] = row[index]
            return self._convert_dict_key(result, topic_name)

    def topic_data_find_(self, where, topic_name):
        table_name = 'topic_' + topic_name
        table = self.get_topic_table_by_name(table_name)
        stmt = self.build_stmt("select", table_name, table)
        stmt = stmt.where(self.build_mysql_where_expression(table, where))
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            res = cursor.fetchall()
        if res is None:
            return None
        else:
            results = []
            for row in res:
                result = {}
                for index, name in enumerate(columns):
                    if isinstance(table.c[name.lower()].type, JSON):
                        if row[index] is not None:
                            result[name] = json.loads(row[index])
                        else:
                            result[name] = None
                    else:
                        result[name] = row[index]
                results.append(result)
            return self._convert_list_elements_key(results, topic_name)

    def topic_data_find_with_aggregate(self, where, topic_name, aggregate):
        table_name = 'topic_' + topic_name
        table = self.get_topic_table_by_name(table_name)
        for key, value in aggregate.items():
            if value == "sum":
                stmt = select(text(f'sum({key.lower()})'))
            elif value == "count":
                stmt = select(func.count())
            elif value == "avg":
                stmt = select(text(f'avg({key.lower()})'))
        stmt = stmt.select_from(table)
        stmt = stmt.where(self.build_mysql_where_expression(table, where))
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            res = cursor.fetchone()
        if res is None:
            return None
        else:
            return res[0]

    def topic_data_list_all(self, topic_name) -> list:
        table_name = 'topic_' + topic_name
        table = self.get_topic_table_by_name(table_name)
        # stmt = select(table)
        stmt = self.build_stmt("select", table_name, table)
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            res = cursor.fetchall()
            if res is None:
                return None
            else:
                results = []
                for row in res:
                    result = {}
                    for index, name in enumerate(columns):
                        if isinstance(table.c[name.lower()].type, JSON):
                            if row[index] is not None:
                                result[name] = json.loads(row[index])
                            else:
                                result[name] = None
                        else:
                            result[name] = row[index]
                    if storage_template.check_topic_type(topic_name) == "raw":
                        results.append(result['data_'])
                    else:
                        results.append(result)
                if storage_template.check_topic_type(topic_name) == "raw":
                    return results
                else:
                    return self._convert_list_elements_key(results, topic_name)

    def topic_data_page_(self, where, sort, pageable, model, name) -> DataPage:
        table_name = build_collection_name(name)
        count = self.count_topic_data_table(table_name)
        table = self.get_topic_table_by_name(table_name)
        stmt = self.build_stmt("select", table_name, table)
        stmt = stmt.where(self.build_mysql_where_expression(table, where))
        orders = self.build_mysql_order(table, sort)
        for order in orders:
            stmt = stmt.order_by(order)
        offset = pageable.pageSize * (pageable.pageNumber - 1)
        stmt = stmt.offset(offset).limit(pageable.pageSize)
        results = []
        with self.engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            res = cursor.fetchall()
        if storage_template.check_topic_type(name) == "raw":
            for row in res:
                result = {}
                for index, name in enumerate(columns):
                    if name == "data_":
                        result.update(json.loads(row[index]))
                    results.append(result)
        else:
            for row in res:
                result = {}
                for index, name in enumerate(columns):
                    if isinstance(table.c[name.lower()].type, JSON):
                        if row[index] is not None:
                            result[name] = json.loads(row[index])
                        else:
                            result[name] = None
                    else:
                        result[name] = row[index]
                if model is not None:
                    results.append(parse_obj(model, result, table))
                else:
                    results.append(result)
        return build_data_pages(pageable, results, count)

    '''
        internal method
    '''

    def get_table_column_default_value(self, table_name, column_name):
        columns = self._get_table_columns(table_name)
        for column in columns:
            if column["name"] == column_name:
                return column["default"]

    def _get_table_columns(self, table_name):
        cached_columns = cacheman[COLUMNS_BY_TABLE_NAME].get(table_name)
        if cached_columns is not None:
            return cached_columns
        columns = self.insp.get_columns(table_name)
        if columns is not None:
            cacheman[COLUMNS_BY_TABLE_NAME].set(table_name, columns)
            return columns

    @staticmethod
    def _convert_list_elements_key(list_info, topic_name):
        if list_info is None:
            return None
        new_dict = {}
        new_list = []
        factors = storage_template.get_topic_factors(topic_name)
        for item in list_info:
            for factor in factors:
                new_dict[factor['name']] = item[factor['name'].lower()]
                new_dict['id_'] = item['id_']
                if 'tenant_id_' in item:
                    new_dict['tenant_id_'] = item.get("tenant_id_", 1)
                if "insert_time_" in item:
                    new_dict['insert_time_'] = item.get("insert_time_", datetime.now().replace(tzinfo=None))
                if "update_time_" in item:
                    new_dict['update_time_'] = item.get("update_time_", datetime.now().replace(tzinfo=None))
                if "version_" in item:
                    new_dict['version_'] = item.get("version_", 0)
                if "aggregate_assist_" in item:
                    new_dict['aggregate_assist_'] = item.get("aggregate_assist_")
            new_list.append(new_dict)
        return new_list

    @staticmethod
    def _convert_dict_key(dict_info, topic_name):
        if dict_info is None:
            return None
        new_dict = {}
        factors = storage_template.get_topic_factors(topic_name)
        for factor in factors:
            new_dict[factor['name']] = dict_info[factor['name'].lower()]
        new_dict['id_'] = dict_info['id_']
        if 'tenant_id_' in dict_info:
            new_dict['tenant_id_'] = dict_info.get("tenant_id_", 1)
        if "insert_time_" in dict_info:
            new_dict['insert_time_'] = dict_info.get("insert_time_", datetime.now().replace(tzinfo=None))
        if "update_time_" in dict_info:
            new_dict['update_time_'] = dict_info.get("update_time_", datetime.now().replace(tzinfo=None))
        if "version_" in dict_info:
            new_dict['version_'] = dict_info.get("version_", None)
        if "aggregate_assist_" in dict_info:
            new_dict['aggregate_assist_'] = dict_info.get("aggregate_assist_")
        return new_dict

    def count_topic_data_table(self, table_name):
        stmt = 'SELECT count(%s) AS count FROM %s' % ('id_', table_name)
        with self.engine.connect() as conn:
            cursor = conn.execute(text(stmt)).cursor
            columns = [col[0] for col in cursor.description]
            cursor.rowfactory = lambda *args: dict(zip(columns, args))
            result = cursor.fetchone()
        return result['COUNT']


