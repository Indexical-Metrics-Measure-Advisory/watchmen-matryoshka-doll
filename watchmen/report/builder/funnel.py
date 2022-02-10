from decimal import Decimal
from typing import List

import arrow
from model.model.report.column import Column
from model.model.report.report import ReportFunnel, ReportFunnelType
from pypika import Criterion, Field, AliasedQuery
from pypika.terms import LiteralValue

from watchmen.common.presto import presto_fn
from watchmen.report.builder.utils import convent_column_list_to_dict


def build_report_funnels(funnels: List[ReportFunnel], dataset_query_alias, dataset_columns: List[Column]):
    columns = convent_column_list_to_dict(dataset_columns)
    criterions = []
    for funnel in funnels:
        if funnel.enabled:
            column = columns.get(funnel.columnId)
            field = Field(column.alias, None, AliasedQuery(dataset_query_alias))
            if funnel.type == ReportFunnelType.NUMERIC:
                if funnel.range:
                    if check_funnel_values(funnel.values, True):
                        lower = Decimal(funnel.values[0])
                        upper = Decimal(funnel.values[1])
                        criterions.append(field.between(lower, upper))
                else:
                    if check_funnel_values(funnel.values, False):
                        criterions.append(field.eq(Decimal(funnel.values[0])))
            elif funnel.type == ReportFunnelType.DATE:
                if funnel.range:
                    if check_funnel_values(funnel.values, True):
                        lower_value = funnel.values[0]
                        upper_value = funnel.values[1]
                        lower = LiteralValue("DATE \'{0}\'".format(arrow.get(lower_value).format('YYYY-MM-DD')))
                        upper = LiteralValue("DATE \'{0}\'".format(arrow.get(upper_value).format('YYYY-MM-DD')))
                        criterions.append(field.between(lower, upper))
                else:
                    if check_funnel_values(funnel.values, False):
                        value = LiteralValue("DATE \'{0}\'".format(arrow.get(funnel.values[0]).format('YYYY-MM-DD')))
                        criterions.append(field.eq(value))
            elif funnel.type == ReportFunnelType.YEAR:
                if funnel.range:
                    if check_funnel_values(funnel.values, True):
                        lower = Decimal(funnel.values[0])
                        upper = Decimal(funnel.values[1])
                        criterions.append(presto_fn.PrestoYear(field).between(lower, upper))
                else:
                    if check_funnel_values(funnel.values, False):
                        value = Decimal(funnel.values[0])
                        criterions.append(presto_fn.PrestoYear(field).eq(value))
            elif funnel.type == ReportFunnelType.MONTH:
                if funnel.range:
                    if check_funnel_values(funnel.values, True):
                        lower = Decimal(funnel.values[0])
                        upper = Decimal(funnel.values[1])
                        criterions.append(presto_fn.PrestoMonth(field).between(lower, upper))
                else:
                    if check_funnel_values(funnel.values, False):
                        value = Decimal(funnel.values[0])
                        criterions.append(presto_fn.PrestoMonth(field).eq(value))
            else:
                raise NotImplementedError("funnel type is not supported")
    return Criterion.all(criterions)


def check_funnel_values(values, is_range):
    if values:
        if is_range:
            if len(values) != 2:
                return False
            else:
                value1 = values[0]
                value2 = values[1]
                if value1 and value2:
                    return True
        else:
            if len(values) != 1:
                return False
            else:
                value = values[0]
                if value:
                    return True
    else:
        return False

