from decimal import Decimal
from typing import List

from arrow import arrow
from pypika import Schema, Table, Field
from pypika.terms import Term, Criterion, LiteralValue

from model.model.common.parameter import Parameter, ParameterJoint
from watchmen.common.utils.data_utils import build_collection_name
from model.model.console_space.console_space import SubjectDataSetFilter
from watchmen.console_space.storage.console_space_storage import load_console_space_by_subject_id
from watchmen.database.datasource.storage.data_source_storage import load_data_source_by_id
from watchmen.pipeline.utils.units_func import get_factor
from watchmen.report.builder.dialects import PrestoQuery
from watchmen.report.builder.utils import build_table_by_topic_id
from model.model.space.space import SpaceFilter
from watchmen.space.storage.space_storage import get_filters_by_id
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def get_topic_sub_query_with_space_filter(console_subject, current_user):
    console_space = load_console_space_by_subject_id(console_subject.subjectId, current_user)
    filters: List[SpaceFilter] = get_filters_by_id(console_space.spaceId, current_user)
    if filters is None:
        filters = []
    topic_sub_query = {}
    for filter in filters:
        if filter.enabled:
            topic = get_topic_by_id(filter.topicId)
            table = build_table_by_topic_id(filter.topicId)
            sub_query = PrestoQuery. \
                from_(table). \
                select('*'). \
                where(build_space_filter_where(filter.joint))
            # where(table.tenant_id_ == current_user.tenantId). \
            topic_sub_query[filter.topicId] = {"alias": topic.name, "query": sub_query}

    def get_topic_sub_query_by_topic_id(topic_id):
        return topic_sub_query.get(topic_id, None)

    return get_topic_sub_query_by_topic_id


def build_space_filter_where(filter: ParameterJoint):
    if filter.jointType:
        if filter.jointType == "and":
            return Criterion.all([build_space_filter_where(item) for item in filter.filters])
        elif filter.jointType == "or":
            return Criterion.any([build_space_filter_where(item) for item in filter.filters])
    else:
        return build_space_filter_criterion(filter)


def build_space_filter_criterion(filter: SubjectDataSetFilter) -> Criterion:
    operator_ = filter.operator
    left = parse_space_filter_parameter(filter.left)
    right = parse_space_filter_parameter(filter.right)

    lvalue = left["value"]
    ltype = left["type"]
    rvalue = right["value"]

    if ltype == "number":
        if operator_ == "in" or operator_ == "not-in":
            right_value_list = rvalue.split(",")
            right_value_trans_list = []
            for value_ in right_value_list:
                if value_.isdigit():
                    right_value_trans_list.append(Decimal(value_))
            return build_space_filter_criterion_expression(operator_, lvalue, right_value_trans_list)
        else:
            right_trans_value = Decimal(rvalue)
            return build_space_filter_criterion_expression(operator_, lvalue, right_trans_value)
    if ltype == "date":
        return build_space_filter_criterion_expression(operator_, lvalue, LiteralValue(
            "DATE \'{0}\'".format(arrow.get(rvalue).format('YYYY-MM-DD'))))
    elif ltype == "datetime":
        return build_space_filter_criterion_expression(operator_, lvalue,
                                                       LiteralValue("timestamp \'{0}\'".format(
                                                           arrow.get(rvalue).format('YYYY-MM-DD HH:mm:ss'))))
    else:
        return build_space_filter_criterion_expression(operator_, lvalue, rvalue)


def build_space_filter_criterion_expression(operator_, left, right):
    if operator_ == "equals":
        return left.eq(right)
    elif operator_ == "not-equals":
        return left.ne(right)
    elif operator_ == 'empty':
        return left.isnull()
    elif operator_ == 'not-empty':
        return left.notnull()
    elif operator_ == "more":
        return left.gt(right)
    elif operator_ == "more-equals":
        return left.gte(right)
    elif operator_ == "less":
        return left.lt(right)
    elif operator_ == "less-equals":
        return left.lte(right)
    elif operator_ == 'in':
        return left.isin(right)
    elif operator_ == 'not-in':
        return left.notin(right)
    else:
        # TODO more operator support
        raise NotImplementedError("filter operator is not supported")


def parse_space_filter_parameter(parameter: Parameter, ):
    if parameter.kind == "topic":
        topic = get_topic_by_id(parameter.topicId)
        topic_col_name = build_collection_name(topic.name)
        datasource = load_data_source_by_id(topic.dataSourceId)
        catalog_name = datasource.dataSourceCode
        schema_name = datasource.name
        schema = Schema(schema_name, LiteralValue(catalog_name))
        table = Table(topic_col_name, schema)
        factor = get_factor(parameter.factorId, topic)
        field = Field(factor.name, None, table)
        return {"value": field, "type": factor.type}
    elif parameter.kind == 'constant':
        return {"value": Term.wrap_constant(parameter.value), "type": "text"}
