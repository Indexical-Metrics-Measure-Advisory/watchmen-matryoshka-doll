from decimal import Decimal
from typing import List

from watchmen.common.presto import presto_fn
import arrow
from model.model.common.parameter import Parameter, ParameterJoint
from model.model.console_space.console_space import SubjectDataSetFilter
from model.model.report.column import Column, Operator
from pypika import Table, Schema, Field, Criterion, CustomFunction, AliasedQuery
from pypika.enums import Arithmetic
from pypika.terms import PseudoColumn, ArithmeticExpression, Term, ValueWrapper, LiteralValue
from watchmen_boot.storage.model.data_source import DataSource

from watchmen.common.utils.data_utils import build_collection_name
from watchmen.database.datasource.storage.data_source_storage import load_data_source_by_id
from watchmen.pipeline.utils.units_func import get_factor, get_factor_by_name
from watchmen.report.builder.utils import transform_value_str_to_number, build_table_by_topic_id
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id, load_topic_by_name


def build_dataset_select_fields(columns: List[Column], topic_space_filter) -> List[Field]:
    fields = []
    for column in columns:
        # print(column)
        result = dataset_parse_parameter(column.parameter, topic_space_filter)
        field: Field = result["value"]
        if "computed_type" in result and result["computed_type"] == "month-of":

            fields.append(field.as_(column.alias))
        elif check_column_type_is_date(column.parameter):
            date_fnc = CustomFunction("date", ["col1"])
            fields.append(date_fnc(field).as_(column.alias))
        else:
            fields.append(field.as_(column.alias))

    return fields


def check_column_type_is_date(parameter: Parameter):
    topic = get_topic_by_id(parameter.topicId)
    factor = get_factor(parameter.factorId, topic)
    if factor.type == "date":
        return True


def dataset_parse_parameter(parameter: Parameter, topic_space_filter):
    # print(parameter)
    if parameter.kind   == "topic":
        topic = get_topic_by_id(parameter.topicId)
        alias_table = topic_space_filter(parameter.topicId)
        if alias_table:
            table = AliasedQuery(alias_table["alias"])
        else:
            topic_col_name = build_collection_name(topic.name)
            datasource: DataSource = load_data_source_by_id(topic.dataSourceId)
            catalog_name = datasource.dataSourceCode
            schema_name = datasource.name
            schema = Schema(schema_name, LiteralValue(catalog_name))
            table = Table(topic_col_name, schema)
        factor = get_factor(parameter.factorId, topic)
        field = Field(factor.name, None, table)
        return {"value": field, "type": factor.type}
    elif parameter.kind == 'constant':
        if parameter.value.strip().startswith("{&"):
            func_, type_ = build_function(parameter.value, topic_space_filter)
            return {"value": func_, "type": type_}
        else:
            return {"value": Term.wrap_constant(parameter.value), "type": "text"}
    elif parameter.kind == 'computed':
        left = None
        if parameter.type == "month-of":
            topic_factor = parameter.parameters[0]
            topic = get_topic_by_id(topic_factor.topicId)
            factor = get_factor(topic_factor.factorId, topic)
            # print(factor)
            alias_table = topic_space_filter(topic_factor.topicId)
            if alias_table:
                table = AliasedQuery(alias_table["alias"])
            else:
                topic_col_name = build_collection_name(topic.name)
                datasource: DataSource = load_data_source_by_id(topic.dataSourceId)
                catalog_name = datasource.dataSourceCode
                schema_name = datasource.name
                schema = Schema(schema_name, LiteralValue(catalog_name))
                table = Table(topic_col_name, schema)

            return {"value": presto_fn.PrestoMonth(Field(factor.name, table=table)), "type": factor.type, "computed_type": "month-of"}
        else:
            for item in parameter.parameters:
                if left is not None:
                    right = dataset_parse_parameter(item, topic_space_filter)
                    return {"value": build_arithmetic_expression(parameter.type, left, right),
                            "type": "number"}
                else:
                    left = dataset_parse_parameter(item, topic_space_filter)
                    # return {"value": build_arithmetic_expression(parameter.type, left, right),
                    #         "type": "number"}


def build_function(func_expr_str: str, topic_space_filter):
    if func_expr_str.strip().startswith("{&monthDiff"):
        value_ = func_expr_str.strip()
        args_str = value_.replace("{&monthDiff(", "").replace(")}", "")
        func = _date_diff("month", args_str, topic_space_filter)
        return func, "number"
    elif func_expr_str.strip().startswith("{&dayDiff"):
        value_ = func_expr_str.strip()
        args_str = value_.replace("{&dayDiff(", "").replace(")}", "")
        func = _date_diff("day", args_str, topic_space_filter)
        return func, "number"
    elif func_expr_str.strip().startswith("{&yearDiff"):
        value_ = func_expr_str.strip()
        args_str = value_.replace("{&yearDiff(", "").replace(")}", "")
        func = _date_diff("year", args_str, topic_space_filter)
        return func, "number"
    else:
        raise NotImplementedError()


def _date_diff(unit, args_str, topic_space_filter):
    args_list = args_str.split(",")
    if len(args_list) != 2:
        raise ValueError("Date_diff have invalid args", args_list)
    date_diff = CustomFunction("DATE_DIFF", ["col1", "col2", "col3"])
    arg1 = args_list[0].strip()
    arg2 = args_list[1].strip()
    date1 = _process_date_diff_arg(arg1, topic_space_filter)
    date2 = _process_date_diff_arg(arg2, topic_space_filter)
    return date_diff(unit, date1, date2)


def _process_date_diff_arg(arg, topic_space_filter):
    date_fnc = CustomFunction("date", ["col1"])
    if arg == "now":
        date = PseudoColumn('current_date')
    else:
        if "." in arg:
            arg_list = arg.split(".")
            topic_name = arg_list[0].strip()
            topic = load_topic_by_name(topic_name)
            alias_table = topic_space_filter(topic.topicId)
            if alias_table:
                table = AliasedQuery(alias_table["alias"])
            else:
                table = build_table_by_topic_id(topic.topicId)
            factor_name = arg_list[1].strip()
            factor = get_factor_by_name(factor_name, topic)
            date = Field(factor.name, None, table)
        else:
            date = date_fnc(arg)
    return date


def build_arithmetic_expression(operator_, left, right):
    if isinstance(left, ValueWrapper):
        left.value = transform_value_str_to_number(left.value)

    if isinstance(right, ValueWrapper):
        right.value = transform_value_str_to_number(right.value)

    if operator_ == Operator.add:
        return ArithmeticExpression(Arithmetic.add, left, right)
    elif operator_ == Operator.subtract:
        return ArithmeticExpression(Arithmetic.sub, left, right)
    elif operator_ == Operator.multiply:
        return ArithmeticExpression(Arithmetic.mul, left, right)
    elif operator_ == Operator.divide:
        return ArithmeticExpression(Arithmetic.div, left, right)


def build_dataset_where(filter: ParameterJoint, topic_space_filter):
    if filter.jointType:
        if filter.jointType == "and":
            return Criterion.all([build_dataset_where(item, topic_space_filter) for item in filter.filters])
        elif filter.jointType == "or":
            return Criterion.any([build_dataset_where(item, topic_space_filter) for item in filter.filters])
    else:
        return build_criterion(filter, topic_space_filter)


def build_criterion(filter: SubjectDataSetFilter, topic_space_filter) -> Criterion:
    operator_ = filter.operator
    left = dataset_parse_parameter(filter.left, topic_space_filter)
    right = dataset_parse_parameter(filter.right, topic_space_filter)

    lvalue = left["value"]
    ltype = left["type"]

    rvalue = right["value"]
    rtype = right["type"]

    if operator_ == "empty" or operator_ == "not-empty":
        return _build_criterion_expression(operator_, lvalue, rvalue)
    if ltype == rtype:
        if operator_ == "in" or operator_ == "not-in":
            if ltype == "number":
                if isinstance(rvalue, ValueWrapper):
                    value = rvalue.value
                    right_value_list = value.split(",")
                    right_value_trans_list = []
                    for value_ in right_value_list:
                        if value_.isdigit():
                            right_value_trans_list.append(Decimal(value_))
                    return _build_criterion_expression(operator_, lvalue, right_value_trans_list)
            else:
                if isinstance(rvalue, ValueWrapper):
                    value = rvalue.value
                    right_value_list = value.split(",")
                    right_value_trans_list = []
                    for value_ in right_value_list:
                        right_value_trans_list.append(value_)
                    return _build_criterion_expression(operator_, lvalue, right_value_trans_list)
        else:
            return _build_criterion_expression(operator_, lvalue, rvalue)
    else:
        if ltype == "number" and rtype == "text":
            if operator_ == "in" or operator_ == "not-in":
                if isinstance(rvalue, ValueWrapper):
                    value = rvalue.value
                    right_value_list = value.split(",")
                    right_value_trans_list = []
                    for value_ in right_value_list:
                        if value_.isdigit():
                            right_value_trans_list.append(Decimal(value_))
                    return _build_criterion_expression(operator_, lvalue, right_value_trans_list)
            else:
                if isinstance(rvalue, ValueWrapper):
                    value = rvalue.value
                    right_trans_value = Decimal(value)
                    return _build_criterion_expression(operator_, lvalue, right_trans_value)
                else:
                    return _build_criterion_expression(operator_, lvalue, rvalue)
        if ltype == "date" and rtype == "text":
            if isinstance(rvalue, ValueWrapper):
                value = rvalue.value
                return _build_criterion_expression(operator_, lvalue, LiteralValue(
                    "DATE \'{0}\'".format(arrow.get(value).format('YYYY-MM-DD'))))
        elif ltype == "datetime" and rtype == "text":
            return _build_criterion_expression(operator_, lvalue,
                                               LiteralValue("timestamp \'{0}\'".format(
                                                   arrow.get(rvalue.value).format('YYYY-MM-DD HH:mm:ss'))))
        else:
            return _build_criterion_expression(operator_, lvalue, rvalue)


def _build_criterion_expression(operator_, left, right):
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
