from decimal import Decimal
from typing import List

import arrow
from pypika import Criterion, AliasedQuery, Field
from pypika.terms import LiteralValue

from watchmen.pipeline.utils.units_func import get_factor
from model.model.report.column import Column
from model.model.report.report import ReportFunnel
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def build_report_funnels(funnels: List[ReportFunnel], dataset_columns: List[Column], dataset_query_alias):
    columns = convent_column_list_to_dict(dataset_columns)
    criterions = []
    for funnel in funnels:
        if funnel.enabled:
            column = columns.get(funnel.columnId)
            field: Field = parse_column_parameter(column.parameter, dataset_query_alias)["value"]
            if funnel.type == "numeric":
                if funnel.range:
                    lower = Decimal(funnel.values[0])
                    upper = Decimal(funnel.values[1])
                    criterions.append(field.between(lower, upper))
                else:
                    if funnel.values:
                        criterions.append(field.eq(Decimal(funnel.values[0])))
            elif funnel.type == "date":
                if funnel.range:
                    lower = LiteralValue("DATE \'{0}\'".format(arrow.get(funnel.values[0]).format('YYYY-MM-DD')))
                    upper = LiteralValue("DATE \'{0}\'".format(arrow.get(funnel.values[1]).format('YYYY-MM-DD')))
                    criterions.append(field.between(lower, upper))
                else:
                    value = LiteralValue("DATE \'{0}\'".format(arrow.get(funnel.values[0]).format('YYYY-MM-DD')))
                    criterions.append(field.eq(value))
            else:
                if funnel.range:
                    lower = LiteralValue(funnel.values[0])
                    upper = LiteralValue(funnel.values[1])
                    criterions.append(field.between(lower, upper))
                else:
                    value = LiteralValue(funnel.values[0])
                    if value:
                        criterions.append(field.eq(value))
        return Criterion.all(criterions)


def convent_column_list_to_dict(columns) -> dict:
    columns_dict = {}
    for column in columns:
        columns_dict[column.columnId] = column
    return columns_dict


def parse_column_parameter(parameter, dataset_query_alias):
    if parameter.kind == "topic":
        topic = get_topic_by_id(parameter.topicId)
        table = AliasedQuery(dataset_query_alias)
        factor = get_factor(parameter.factorId, topic)
        field = Field(factor.name, None, table)
        return {"value": field, "type": factor.type}
