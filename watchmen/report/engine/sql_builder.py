from typing import List

from pypika import Query, Table, Field, JoinType, Criterion
from pypika.queries import QueryBuilder
import operator

from watchmen.common.utils.data_utils import build_collection_name
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.report.model.column import Column, Operator
from watchmen.report.model.filter import Filter, ConnectiveType
from watchmen.report.model.join import Join, JoinType
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


# def build_query(columns: List[Column], joins: List[Join], filters: List[Filter]) -> str:


def _from(column: Column) -> QueryBuilder:
    topic = get_topic_by_id(column.topicId)
    topic_col_name = build_collection_name(topic.name)
    return Query.from_(Table(topic_col_name))


def _select(q: QueryBuilder, column: Column) -> QueryBuilder:
    # get topic and factor
    topic = get_topic_by_id(column.topicId)
    topic_col_name = build_collection_name(topic.name)
    factor = get_factor(column.factorId, topic)

    if column.operator is None:
        if column.alias is None:
            return q.select(Table(topic_col_name)[factor.name])
        else:
            return q.select(Table(topic_col_name)[factor.name].as_(column.alias))
    else:
        sec_topic = get_topic_by_id(column.secondaryTopicId)
        sec_topic_col_name = build_collection_name(sec_topic.name)
        sec_factor = get_factor(column.secondaryFactorId, sec_topic)

        if column.operator == Operator.add:
            if column.alias is None:
                return q.select(
                    Field(Table(topic_col_name)[factor.name]) + Field(Table(sec_topic_col_name)[sec_factor.name]))
            else:
                return q.select((Field(Table(topic_col_name)[factor.name]) + Field(
                    Table(sec_topic_col_name)[sec_factor.name])).as_(column.alias))

        if column.operator == Operator.subtract:
            if column.alias is None:
                return q.select(
                    Field(Table(topic_col_name)[factor.name]) - Field(Table(sec_topic_col_name)[sec_factor.name]))
            else:
                return q.select((Field(Table(topic_col_name)[factor.name]) - Field(
                    Table(sec_topic_col_name)[sec_factor.name])).as_(column.alias))

        if column.operator == Operator.multiply:
            if column.alias is None:
                return q.select(
                    Field(Table(topic_col_name)[factor.name]) * Field(Table(sec_topic_col_name)[sec_factor.name]))
            else:
                return q.select(
                    (Field(Table(topic_col_name)[factor.name]) * Field(
                        Table(sec_topic_col_name)[sec_factor.name])).as_(
                        column.alias))

        if column.operator == Operator.divide:
            if column.alias is None:
                return q.select(
                    Field(Table(topic_col_name)[factor.name]) / Field(Table(sec_topic_col_name)[sec_factor.name]))
            else:
                return q.select(
                    (Field(Table(topic_col_name)[factor.name]) / Field(
                        Table(sec_topic_col_name)[sec_factor.name])).as_(
                        column.alias))

        if column.operator == Operator.modulus:
            if column.alias is None:
                return q.select(operator.mod(Field(Table(topic_col_name)[factor.name]),
                                             Field(Table(sec_topic_col_name)[sec_factor.name])))
            else:
                return q.select(
                    (Field(Table(topic_col_name)[factor.name]) % Field(
                        Table(sec_topic_col_name)[sec_factor.name])).as_(
                        column.alias))


def _join(q: QueryBuilder, join: Join) -> QueryBuilder:
    # left
    topic = get_topic_by_id(join.topicId)
    topic_col_name = build_collection_name(topic.name)
    factor = get_factor(join.factorId, topic)
    left_table = Table(topic_col_name)

    # right
    sec_topic = get_topic_by_id(join.secondaryTopicId)
    sec_topic_col_name = build_collection_name(sec_topic.name)
    sec_factor = get_factor(join.secondaryFactorId, sec_topic)
    right_table = Table(sec_topic_col_name)

    if join.type == JoinType.inner:
        return q.join(right_table, JoinType.inner).on(
            operator.eq(left_table[factor.name], right_table[sec_factor.name]))

    if join.type == JoinType.left:
        return q.join(right_table, JoinType.left).on(
            operator.eq(left_table[factor.name], right_table[sec_factor.name]))

    if join.type == JoinType.right:
        return q.join(right_table, JoinType.right).on(
            operator.eq(left_table[factor.name], right_table[sec_factor.name]))


def _connective_filter(q: QueryBuilder, filters: List[Filter], jointType) -> QueryBuilder:
    criterion_list: List = []
    for item in filters:
        criterion_list.append(_filter_criterion(item))

    if jointType == ConnectiveType.and_type:
        return q.where(Criterion.all(criterion_list))

    if jointType == ConnectiveType.or_type:
        return q.where(Criterion.any(criterion_list))


def _filter_criterion(filter: Filter) -> any:
    topic = get_topic_by_id(filter.topicId)
    table = Table(build_collection_name(topic.name))
    factor = get_factor(filter.factorId, topic)

    if filter.operator == "equals":
        return operator.eq(table[factor.name], filter.value)
    elif filter.operator == "not-equals":
        return operator.ne(table[factor.name], filter.value)
    elif filter.operator == "more":
        return operator.gt(table[factor.name], int(filter.value))
    elif filter.operator == "more-equals":
        return operator.ge(table[factor.name], int(filter.value))
    elif filter.operator == "less":
        return operator.lt(table[factor.name], int(filter.value))
    elif filter.operator == "less-equals":
        return operator.le(table[factor.name], int(filter.value))
    elif filter.operator == "in":
        # todo
        return table[factor.name].isin(['a', 'b'])
    else:
        # TODO more operator support
        raise Exception("operator is not supported")
