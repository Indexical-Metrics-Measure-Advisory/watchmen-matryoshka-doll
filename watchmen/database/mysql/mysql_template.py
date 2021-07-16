from datetime import datetime
import json
import logging
import operator
from decimal import Decimal
from operator import eq

from cacheout import Cache
from sqlalchemy import update, Table, and_, or_, delete, Column, DECIMAL, String, desc, asc, \
    text, func, DateTime, BigInteger, Date, Integer, JSON
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.engine import Inspector
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from watchmen.common.data_page import DataPage
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import build_data_pages, capital_to_lower, build_collection_name
from watchmen.common.utils.data_utils import convert_to_dict
from watchmen.config.config import settings, PROD
from watchmen.database.mysql.mysql_engine import engine
from watchmen.database.mysql.mysql_table_definition import get_table_by_name, metadata, get_topic_table_by_name
from watchmen.database.mysql.mysql_utils import parse_obj, count_table, count_topic_data_table
from watchmen.database.singleton import singleton
from watchmen.database.storage.exception.exception import OptimisticLockError
from watchmen.database.storage.storage_interface import StorageInterface
from watchmen.database.storage.utils.table_utils import get_primary_key

cache = Cache()

cache_column = Cache()
insp = Inspector.from_engine(engine)
# import arrow

log = logging.getLogger("app." + __name__)

log.info("mysql template initialized")


@singleton
class MysqlStorage(StorageInterface):

    def build_mysql_where_expression(self, table, where):
        for key, value in where.items():
            if key == "and" or key == "or":
                if isinstance(value, list):
                    result_filters = []
                    for express in value:
                        result = self.build_mysql_where_expression(table, express)
                        result_filters.append(result)
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
                                if isinstance(v, list):
                                    value_ = ",".join(v)
                                else:
                                    value_ = v
                                stmt = "JSON_CONTAINS(" + key.lower() + ", '[\"" + value_ + "\"]', '$') = 1"
                                return text(stmt)
                            else:
                                if isinstance(v, list):
                                    if len(v) != 0:
                                        return table.c[key.lower()].in_(v)
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

    def build_mysql_updates_expression(self, table, updates, stmt_type: str) -> dict:
        if stmt_type == "insert":
            new_updates = {}
            # print(table.c.keys())
            c_dict = table.c
            for key in c_dict.keys():
                if key == "id_":
                    new_updates[key] = get_surrogate_key()
                elif key == "version_":
                    new_updates[key] = 0
                else:
                    if isinstance(c_dict[key].type, JSON):
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
            c_dict= table.c
            for key in c_dict.keys():
                if key == "version_":
                    new_updates[key] = updates.get(key) + 1
                else:
                    if isinstance(c_dict[key].type, JSON):
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

    def insert_one(self, one, model, name):
        table = get_table_by_name(name)
        one_dict: dict = convert_to_dict(one)
        values = {}
        for key, value in one_dict.items():
            if isinstance(table.c[key.lower()].type, JSON):
                if value is not None:
                    values[key.lower()] = value
                else:
                    values[key.lower()] = None
            else:
                values[key.lower()] = value
        stmt = insert(table).values(values)
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt)
        return model.parse_obj(one)

    def insert_all(self, data, model, name):
        table = get_table_by_name(name)
        stmt = insert(table)
        value_list = []
        for item in data:
            instance_dict: dict = convert_to_dict(item)
            values = {}
            for key in table.c.keys():
                values[key] = instance_dict.get(key)
            value_list.append(values)
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt, value_list)

    def update_one(self, one, model, name) -> any:
        table = get_table_by_name(name)
        stmt = update(table)
        one_dict: dict = convert_to_dict(one)
        primary_key = get_primary_key(name)
        stmt = stmt.where(
            eq(table.c[primary_key.lower()], one_dict.get(primary_key)))
        values = {}
        for key, value in one_dict.items():
            if isinstance(table.c[key.lower()].type, JSON):
                if value is not None:
                    values[key.lower()] = value
                else:
                    values[key.lower()] = None
            else:
                values[key.lower()] = value
        stmt = stmt.values(values)
        with engine.connect() as conn:
            with conn.begin():
                result = conn.execute(stmt)
        return model.parse_obj(one)

    def update_one_first(self, where, updates, model, name):
        table = get_table_by_name(name)
        stmt = update(table)
        stmt = stmt.where(self.build_mysql_where_expression(table, where))
        instance_dict: dict = convert_to_dict(updates)
        values = {}
        for key, value in instance_dict.items():
            if isinstance(table.c[key.lower()].type, JSON):
                if value is not None:
                    values[key.lower()] = value
                else:
                    values[key.lower()] = None
            else:
                values[key.lower()] = value
        stmt = stmt.values(values)
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt)
        return model.parse_obj(updates)

    def update_(self, where, updates, model, name):
        table = get_table_by_name(name)
        stmt = update(table)
        stmt = stmt.where(self.build_mysql_where_expression(table, where))
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

    def pull_update(self, where, updates, model, name):
        results = self.find_(where, model, name)
        updates_dict = convert_to_dict(updates)
        for key, value in updates_dict.items():
            for res in results:
                if isinstance(getattr(res, key), list):
                    setattr(res, key, getattr(res, key).remove(value["in"][0]))
                    self.update_one(res, model, name)

    def delete_by_id(self, id_, name):
        table = get_table_by_name(name)
        key = get_primary_key(name)
        stmt = delete(table).where(eq(table.c[key.lower()], id_))
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt)

    def delete_one(self, where: dict, name: str):
        table = get_table_by_name(name)
        stmt = delete(table).where(self.build_mysql_where_expression(table, where))
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt)

    def delete_(self, where, model, name):
        table = get_table_by_name(name)
        if where is None:
            stmt = delete(table)
        else:
            stmt = delete(table).where(self.build_mysql_where_expression(table, where))
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt)

    def find_by_id(self, id_, model, name):
        table = get_table_by_name(name)
        primary_key = get_primary_key(name)
        stmt = select(table).where(eq(table.c[primary_key.lower()], id_))
        with engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            if row is None:
                return None
            else:
                result = {}
                for index, name in enumerate(columns):
                    result[name] = row[index]
                return parse_obj(model, result, table)

    def find_one(self, where, model, name):
        table = get_table_by_name(name)
        stmt = select(table)
        stmt = stmt.where(self.build_mysql_where_expression(table, where))
        with engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            result = {}
            if row is None:
                return None
            else:
                for index, name in enumerate(columns):
                    result[name] = row[index]
                return parse_obj(model, result, table)

    def find_(self, where: dict, model, name: str) -> list:
        table = get_table_by_name(name)
        stmt = select(table)
        where_expression = self.build_mysql_where_expression(table, where)
        if where_expression is not None:
            stmt = stmt.where(where_expression)
        results = []
        with engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            records = cursor.fetchall()
            if records is None:
                return None
            else:
                for record in records:
                    result = {}
                    for index, name in enumerate(columns):
                        result[name] = record[index]
                    results.append(result)
                return [parse_obj(model, row, table) for row in results]

    def list_all(self, model, name):
        table = get_table_by_name(name)
        stmt = select(table)
        with engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            res = cursor.fetchall()
        results = []
        for row in res:
            result = {}
            for index, name in enumerate(columns):
                result[name] = row[index]
            results.append(parse_obj(model, result, table))
        return results

    def list_(self, where, model, name) -> list:
        table = get_table_by_name(name)
        stmt = select(table).where(self.build_mysql_where_expression(table, where))
        with engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            res = cursor.fetchall()
        results = []
        for row in res:
            result = {}
            for index, name in enumerate(columns):
                result[name] = row[index]
            results.append(parse_obj(model, result, table))
        return results

    def page_all(self, sort, pageable, model, name) -> DataPage:
        count = count_table(name)
        table = get_table_by_name(name)
        stmt = select(table)
        orders = self.build_mysql_order(table, sort)
        for order in orders:
            stmt = stmt.order_by(order)
        offset = pageable.pageSize * (pageable.pageNumber - 1)
        stmt = stmt.offset(offset).limit(pageable.pageSize)
        results = []
        with engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            res = cursor.fetchall()
        for row in res:
            result = {}
            for index, name in enumerate(columns):
                result[name] = row[index]
            results.append(parse_obj(model, result, table))
        return build_data_pages(pageable, results, count)

    def page_(self, where, sort, pageable, model, name) -> DataPage:
        count = count_table(name)
        table = get_table_by_name(name)
        stmt = select(table).where(self.build_mysql_where_expression(table, where))
        orders = self.build_mysql_order(table, sort)
        for order in orders:
            stmt = stmt.order_by(order)
        offset = pageable.pageSize * (pageable.pageNumber - 1)
        stmt = stmt.offset(offset).limit(pageable.pageSize)
        results = []
        with engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            res = cursor.fetchall()
        for row in res:
            result = {}
            for index, name in enumerate(columns):
                result[name] = row[index]
            results.append(parse_obj(model, result, table))
        return build_data_pages(pageable, results, count)

    def clear_metadata(self):
        metadata.clear()

    '''
    topic data interface
    '''

    def drop_(self, topic_name):
        return self.drop_topic_data_table(topic_name)

    def drop_topic_data_table(self, topic_name):
        table_name = 'topic_' + topic_name
        try:
            table = get_topic_table_by_name(table_name)
            table.drop(engine)
        except NoSuchTableError:
            log.warning("drop table \"{0}\" not existed".format(table_name))

    def topic_data_delete_(self, where, topic_name):
        table_name = 'topic_' + topic_name
        table = get_topic_table_by_name(table_name)
        if where is None:
            stmt = delete(table)
        else:
            stmt = delete(table).where(self.build_mysql_where_expression(table, where))
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt)

    def topic_data_insert_one(self, one, topic_name):
        table_name = 'topic_' + topic_name
        table = get_topic_table_by_name(table_name)
        one_dict: dict = capital_to_lower(convert_to_dict(one))
        value = self.build_mysql_updates_expression(table, one_dict, "insert")
        stmt = insert(table)
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt, value)

    def topic_data_insert_(self, data, topic_name):
        table_name = 'topic_' + topic_name
        table = get_topic_table_by_name(table_name)
        values = []
        for instance in data:
            instance_dict: dict = convert_to_dict(instance)
            instance_dict['id_'] = get_surrogate_key()
            value = {}
            for key in table.c.keys():
                value[key] = instance_dict.get(key)
            values.append(value)
        stmt = insert(table)
        with engine.connect() as conn:
            with conn.begin():
                conn.execute(stmt, values)

    def topic_data_update_one(self, id_: str, one: any, topic_name: str):
        table_name = 'topic_' + topic_name
        table = get_topic_table_by_name(table_name)
        stmt = update(table).where(eq(table.c['id_'], id_))
        one_dict = convert_to_dict(one)
        values = self.build_mysql_updates_expression(table, capital_to_lower(one_dict), "update")
        stmt = stmt.values(values)
        with engine.begin() as conn:
            conn.execute(stmt)

    def topic_data_update_one_with_version(self, id_: str, version_: int, one: any, topic_name: str):
        table_name = 'topic_' + topic_name
        table = get_topic_table_by_name(table_name)
        stmt = update(table).where(and_(eq(table.c['id_'], id_), eq(table.c['version_'], version_)))
        one_dict = convert_to_dict(one)
        one_dict['version_'] = version_
        values = self.build_mysql_updates_expression(table, capital_to_lower(one_dict), "update")
        stmt = stmt.values(values)
        with engine.begin() as conn:
            result = conn.execute(stmt)
        if result.rowcount == 0:
            raise OptimisticLockError("Optimistic lock error")

    def topic_data_update_(self, query_dict, instance, topic_name):
        table_name = 'topic_' + topic_name
        table = get_topic_table_by_name(table_name)
        stmt = (update(table).
                where(self.build_mysql_where_expression(table, query_dict)))
        instance_dict: dict = convert_to_dict(instance)
        values = {}
        for key, value in instance_dict.items():
            if key != 'id_':
                if key.lower() in table.c.keys():
                    values[key.lower()] = value
        stmt = stmt.values(values)
        with engine.begin() as conn:
            with conn.begin():
                conn.execute(stmt)

    def topic_data_find_by_id(self, id_: str, topic_name: str) -> any:
        return self.topic_data_find_one({"id_": id_}, topic_name)

    def topic_data_find_one(self, where, topic_name) -> any:
        table_name = 'topic_' + topic_name
        table = get_topic_table_by_name(table_name)
        stmt = select(table).where(self.build_mysql_where_expression(table, where))
        with engine.connect() as conn:
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
        table = get_topic_table_by_name(table_name)
        stmt = select(table).where(self.build_mysql_where_expression(table, where))
        with engine.connect() as conn:
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

    def topic_data_list_all(self, topic_name) -> list:
        table_name = 'topic_' + topic_name
        table = get_topic_table_by_name(table_name)
        stmt = select(table)
        with engine.connect() as conn:
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
                    if self._check_topic_type(topic_name) == "raw":
                        results.append(result['data_'])
                    else:
                        results.append(result)
                if self._check_topic_type(topic_name) == "raw":
                    return results
                else:
                    return self._convert_list_elements_key(results, topic_name)

    def topic_data_page_(self, where, sort, pageable, model, name) -> DataPage:
        table_name = build_collection_name(name)
        count = count_topic_data_table(table_name)
        table = get_topic_table_by_name(table_name)
        stmt = select(table).where(self.build_mysql_where_expression(table, where))
        orders = self.build_mysql_order(table, sort)
        for order in orders:
            stmt = stmt.order_by(order)
        offset = pageable.pageSize * (pageable.pageNumber - 1)
        stmt = stmt.offset(offset).limit(pageable.pageSize)
        results = []
        with engine.connect() as conn:
            cursor = conn.execute(stmt).cursor
            columns = [col[0] for col in cursor.description]
            res = cursor.fetchall()
        if self._check_topic_type(name) == "raw":
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

    def _get_table_column_default_value(self, table_name, column_name):
        columns = self._get_table_columns(table_name)
        for column in columns:
            if column["name"] == column_name:
                return column["default"]

    def _get_table_columns(self, table_name):
        key = table_name
        if key in cache_column and settings.ENVIRONMENT == PROD:
            return cache_column.get(key)
        columns = insp.get_columns(table_name)
        if columns is not None:
            cache_column.set(key, columns)
        return columns

    def _check_topic_type(self, topic_name):
        topic = self._get_topic(topic_name)
        return topic['type']

    def _get_topic_factors(self, topic_name):
        topic = self._get_topic(topic_name)
        factors = topic['factors']
        return factors

    def _get_topic(self, topic_name) -> any:
        if topic_name in cache and settings.ENVIRONMENT == PROD:
            return cache.get(topic_name)
        table = get_table_by_name("topics")
        select_stmt = select(table).where(
            self.build_mysql_where_expression(table, {"name": topic_name}))
        with engine.connect() as conn:
            cursor = conn.execute(select_stmt).cursor
            columns = [col[0] for col in cursor.description]
            row = cursor.fetchone()
            if row is None:
                raise
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
                cache.set(topic_name, result)
                return result

    def _convert_list_elements_key(self, list_info, topic_name):
        if list_info is None:
            return None
        new_dict = {}
        new_list = []
        factors = self._get_topic_factors(topic_name)
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

    def _convert_dict_key(self, dict_info, topic_name):
        if dict_info is None:
            return None
        new_dict = {}
        factors = self._get_topic_factors(topic_name)
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
