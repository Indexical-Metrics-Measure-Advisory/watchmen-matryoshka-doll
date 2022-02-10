from decimal import Decimal
from typing import List, Tuple, Union, Any, Callable, Optional

import arrow
from model.model.report.column import Column
from pypika import CustomFunction, AliasedQuery, Case
from pypika.enums import Arithmetic
from pypika.terms import Term, ArithmeticExpression, Function, ValueWrapper, Field, Criterion, LiteralValue, \
    BasicCriterion, Not, NullCriterion, Mod

from watchmen.common.presto import presto_fn
from watchmen.parser.constants import ParameterValueType, Unit, ComputedFunction, \
    Operator, ComputedCaseFunction
from watchmen.parser.date_utility import date_diff, current_date

from watchmen.parser.parameter import Parameter, ParameterJoint
from watchmen.parser.parameter_parser import ParameterParser, ParseResult, ParameterJointParser
from watchmen.parser.utils import build_table_by_topic_id, transform_value_str_to_number, convert_string_to_constant
from watchmen.pipeline.utils.units_func import get_factor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id, get_topic_by_name


class ConsoleParameterParser(ParameterParser):

    def __init__(self, param: Parameter,
                 topic_space_filter: Optional[Callable[[str], dict]] = None,
                 dataset_query_alias: str = None,
                 dataset_columns: List[Column] = []):
        super().__init__(param)
        self.param = param
        self.topic_space_filter = topic_space_filter
        self.dataset_query_alias = dataset_query_alias
        self.dataset_columns = dataset_columns

    def topic_handle(self) -> Tuple[Field,
                                    ParameterValueType]:
        return self.topic_handler()

    def constant_handle(self) -> Tuple[Union[Field, CustomFunction],
                                       ParameterValueType]:
        return self.constant_handler()

    def computed_handle(self) -> Tuple[Union[Field, CustomFunction],
                                       ParameterValueType]:
        return self.computed_handler()

    def topic_handler(self) -> Tuple[Union[Field, CustomFunction],
                                     ParameterValueType]:

        if self.dataset_query_alias:
            return self.topic_handler_in_sub_query()

        return self.topic_handler_in_dataset()

    def topic_handler_in_dataset(self) -> Tuple[Union[Field, CustomFunction],
                                                ParameterValueType]:
        param = self.param
        topic_id = param.topicId
        factor_id = param.factorId
        topic = get_topic_by_id(topic_id)
        table = None
        if self.topic_space_filter:
            if self.topic_space_filter(param.topicId):
                alias_ = self.topic_space_filter(param.topicId)["alias"]
                table = AliasedQuery(alias_)
        if table is None:
            table = build_table_by_topic_id(topic_id)
        factor = get_factor(factor_id, topic)
        result = Field(factor.name, None, table)
        value_type = factor.type
        return result, value_type

    def topic_handler_in_sub_query(self) -> Tuple[Field,
                                                  ParameterValueType]:
        param = self.param
        for column in self.dataset_columns:
            if column.columnId == param.factorId:
                parser_ = ConsoleParameterParser(column.parameter,
                                                 self.topic_space_filter,
                                                 None,
                                                 [])
                parse_result = parser_.parse_parameter()
                table = AliasedQuery(self.dataset_query_alias)
                field = Field(column.alias, None, table)
                value_type = parse_result.value_type
                return field, value_type

    def constant_handler(self) -> Tuple[CustomFunction,
                                        ParameterValueType]:
        param = self.param
        if param.value.strip().startswith("{&"):
            result, value_type = self.match_function()
            return result, value_type
        else:
            return Term.wrap_constant(param.value), ParameterValueType.TEXT

    def computed_handler(self) -> Tuple[CustomFunction,
                                        ParameterValueType]:
        result, value_type = self.match_computed()
        return result, value_type

    def match_function(self) -> Tuple[CustomFunction, ParameterValueType]:
        param = self.param
        constant_ = param.value
        value_ = constant_.strip()
        if constant_.strip().startswith("{&yearDiff"):
            args_str = value_.replace("{&yearDiff(", "").replace(")}", "")
            arg1, arg2 = self.process_date_diff_args(args_str)
            return date_diff(Unit.YEAR, arg1, arg2), ParameterValueType.NUMBER
        elif constant_.strip().startswith("{&monthDiff"):
            args_str = value_.replace("{&monthDiff(", "").replace(")}", "")
            arg1, arg2 = self.process_date_diff_args(args_str)
            return date_diff(Unit.MONTH, arg1, arg2), ParameterValueType.NUMBER
        elif constant_.strip().startswith("{&dayDiff"):
            args_str = value_.replace("{&dayDiff(", "").replace(")}", "")
            arg1, arg2 = self.process_date_diff_args(args_str)
            return date_diff(Unit.DAY, arg1, arg2), ParameterValueType.NUMBER
        else:
            raise NotImplementedError()

    def process_date_diff_args(self, args: str) -> Tuple[CustomFunction, CustomFunction]:
        arg_list = args.split(",")
        if len(arg_list) != 2:
            raise ValueError("Date_diff have invalid args", arg_list)
        result = []
        for arg in arg_list:
            if arg == "now":
                date = current_date()
            else:
                date_fnc = CustomFunction("date", ["col1"])
                if "." in arg:
                    items = arg.split(".")
                    topic_name = items[0].strip()
                    topic = get_topic_by_name(topic_name, None)
                    table = None
                    if self.topic_space_filter:
                        if self.topic_space_filter(self.param.topicId):
                            alias_ = self.topic_space_filter(self.param.topicId)["alias"]
                            table = AliasedQuery(alias_)
                    if table is None:
                        table = build_table_by_topic_id(topic.topicId)
                    factor_name = items[1].strip()
                    date = date_fnc(Field(factor_name, None, table))
                else:
                    date = date_fnc(arg)
            result.append(date)
        return tuple(result)

    def match_computed(self) -> Tuple[Union[ArithmeticExpression, CustomFunction, Function, Case],
                                      ParameterValueType]:
        param = self.param
        type_ = convert_string_to_constant(param.type)
        if type_ in Operator.__members__:
            return self.computed_arithmetic(), ParameterValueType.NUMBER
        elif type_ in ComputedFunction.__members__:
            return self.computed_function(), ParameterValueType.NUMBER
        elif type_ in ComputedCaseFunction.__members__:
            result, value_type = self.computed_case_function()
            return result, value_type

    def computed_arithmetic(self) -> ArithmeticExpression:
        param = self.param
        result = None
        left = None
        for item in param.parameters:
            if left is not None:
                parser = ConsoleParameterParser(item,
                                                self.topic_space_filter,
                                                self.dataset_query_alias,
                                                self.dataset_columns)
                right = parser.parse_parameter()
                result = self.build_arithmetic_expression(param.type, left, right)
            else:
                parser = ConsoleParameterParser(item,
                                                self.topic_space_filter,
                                                self.dataset_query_alias,
                                                self.dataset_columns)
                left = parser.parse_parameter()
        return result

    @staticmethod
    def build_arithmetic_expression(operator_: Operator,
                                    left: ParseResult,
                                    right: ParseResult) -> Union[ArithmeticExpression, Mod]:
        left_obj = left.result
        left_value_type = left.value_type
        right_obj = right.result
        right_value_type = right.value_type
        if isinstance(left_obj, ValueWrapper) and left_value_type == ParameterValueType.TEXT:
            left_obj.value = transform_value_str_to_number(left_obj.value)
        if isinstance(right_obj, ValueWrapper) and right_value_type == ParameterValueType.TEXT:
            right_obj.value = transform_value_str_to_number(right_obj.value)
        if operator_ == Operator.ADD:
            return ArithmeticExpression(Arithmetic.add, left_obj, right_obj)
        elif operator_ == Operator.SUBTRACT:
            return ArithmeticExpression(Arithmetic.sub, left_obj, right_obj)
        elif operator_ == Operator.MULTIPLY:
            return ArithmeticExpression(Arithmetic.mul, left_obj, right_obj)
        elif operator_ == Operator.DIVIDE:
            return ArithmeticExpression(Arithmetic.div, left_obj, right_obj)
        elif operator_ == Operator.MODULUS:
            return left_obj % right_obj

    def computed_function(self) -> Function:
        param = self.param
        parse_result = ConsoleParameterParser(param.parameters[0],
                                              self.topic_space_filter,
                                              self.dataset_query_alias,
                                              self.dataset_columns).parse_parameter()
        if param.type == ComputedFunction.YEAR_OF:
            return presto_fn.PrestoYear(parse_result.result)
        elif param.type == ComputedFunction.MONTH_OF:
            return presto_fn.PrestoMonth(parse_result.result)
        elif param.type == ComputedFunction.WEEK_OF_YEAR:
            return presto_fn.PrestoWeek(parse_result.result)
        elif param.type == ComputedFunction.DAY_OF_WEEK:
            return presto_fn.PrestoDayOfWeek(parse_result.result)
        elif param.type == ComputedFunction.WEEK_OF_MONTH:
            raise Exception("operator is not supported")
        elif param.type == ComputedFunction.QUARTER_OF:
            return presto_fn.PrestoQuarter(parse_result.result)
        elif param.type == ComputedFunction.HALF_YEAR_OF:
            raise Exception("operator is not supported")
        elif param.type == ComputedFunction.DAY_OF_MONTH:
            return presto_fn.PrestoDayOfMonth(parse_result.result)
        else:
            raise Exception("operator is not supported")

    def computed_case_function(self) -> Tuple[Case, ParameterValueType]:
        parameters = self.param.parameters
        case_ = Case()
        value_type = None
        for param in parameters:
            if param.on:
                param_joint_parser = ConsoleParameterJointParser(param.on, self.topic_space_filter)
                condition_ = param_joint_parser.parse_parameter_joint()
                if condition_:
                    param_parser = ConsoleParameterParser(param,
                                                          self.topic_space_filter,
                                                          self.dataset_query_alias,
                                                          self.dataset_columns)
                    param_parser_result = param_parser.parse_parameter()
                    if param_parser_result.result:
                        then_ = param_parser_result.result
                        case_ = case_.when(condition_, then_)
                        value_type = param_parser_result.value_type
            else:
                param_parser = ConsoleParameterParser(param,
                                                      self.topic_space_filter,
                                                      self.dataset_query_alias,
                                                      self.dataset_columns)
                param_parser_result = param_parser.parse_parameter()
                if param_parser_result.result:
                    default_ = param_parser_result.result
                    case_ = case_.else_(default_)
                    value_type = param_parser_result.value_type
        return case_, value_type


class ConsoleParameterJointParser(ParameterJointParser):

    def __init__(self, parameter_joint: ParameterJoint,
                 topic_space_filter: Optional[Callable[[str], dict]] = None,
                 dataset_query_alias: str = None,
                 dataset_columns: List[Column] = []):
        super().__init__(parameter_joint)
        self.parameter_joint = parameter_joint
        self.topic_space_filter = topic_space_filter
        self.dataset_query_alias = dataset_query_alias
        self.dataset_columns = dataset_columns

    def parse_joint(self) -> Criterion:
        param_joint = self.parameter_joint
        if param_joint.jointType == "and":
            return self.parse_joint_and()
        elif param_joint.jointType == "or":
            return self.parse_joint_or()

    def parse_joint_and(self) -> Criterion:
        return Criterion.all(self.parse_filters(self.parameter_joint.filters))

    def parse_joint_or(self) -> Criterion:
        return Criterion.any(self.parse_filters(self.parameter_joint.filters))

    def parse_filters(self, filters: List[ParameterJoint]) -> List:
        results = []
        for item in filters:
            parser_ = ConsoleParameterJointParser(item,
                                                  self.topic_space_filter,
                                                  self.dataset_query_alias,
                                                  self.dataset_columns)
            result = parser_.parse_parameter_joint()
            results.append(result)
        return results

    def parse_criterion(self) -> Any:
        filter_ = self.parameter_joint
        operator_ = filter_.operator

        left_parser = ConsoleParameterParser(filter_.left,
                                             self.topic_space_filter,
                                             self.dataset_query_alias,
                                             self.dataset_columns)
        left_parser_result = left_parser.parse_parameter()

        right_parser = ConsoleParameterParser(filter_.right,
                                              self.topic_space_filter,
                                              self.dataset_query_alias,
                                              self.dataset_columns)
        right_parser_result = right_parser.parse_parameter()

        operator_, left_value, right_value = self.type_inference(operator_, left_parser_result, right_parser_result)
        return self._build_criterion_expression(operator_, left_value, right_value)

    def type_inference(self, operator_, left: ParseResult, right: ParseResult) -> Tuple[str, Any, Any]:
        left_value = left.result
        left_value_type = left.value_type

        right_value = right.result
        right_value_type = right.value_type

        if operator_ == "empty" or operator_ == "not-empty":
            return operator_, left_value, right_value
        if left_value_type == right_value_type:
            if operator_ == "in" or operator_ == "not-in":
                if left_value_type == "number":
                    if isinstance(right_value, ValueWrapper):
                        value = right_value.value
                        right_value_list = value.split(",")
                        right_value_trans_list = []
                        for value_ in right_value_list:
                            if value_.isdigit():
                                right_value_trans_list.append(Decimal(value_))
                        return operator_, left_value, right_value_trans_list
                else:
                    if isinstance(right_value, ValueWrapper):
                        value = right_value.value
                        right_value_list = value.split(",")
                        right_value_trans_list = []
                        for value_ in right_value_list:
                            right_value_trans_list.append(value_)
                        return operator_, left_value, right_value_trans_list
            else:
                return operator_, left_value, right_value
        else:
            if left_value_type == "number" and right_value_type == "text":
                if operator_ == "in" or operator_ == "not-in":
                    if isinstance(right_value, ValueWrapper):
                        value = right_value.value
                        right_value_list = value.split(",")
                        right_value_trans_list = []
                        for value_ in right_value_list:
                            if value_.isdigit():
                                right_value_trans_list.append(Decimal(value_))
                        return operator_, left_value, right_value_trans_list
                else:
                    if isinstance(right_value, ValueWrapper):
                        value = right_value.value
                        right_trans_value = Decimal(value)
                        return operator_, left_value, right_trans_value
                    else:
                        return operator_, left_value, right_value
            if left_value_type == "date" and right_value_type == "text":
                if isinstance(right_value, ValueWrapper):
                    value = right_value.value
                    return operator_, left_value, LiteralValue(
                        "DATE \'{0}\'".format(arrow.get(value).format('YYYY-MM-DD')))
            elif left_value_type == "datetime" and right_value_type == "text":
                if isinstance(right_value, ValueWrapper):
                    return operator_, \
                           left_value, \
                           LiteralValue("timestamp \'{0}\'".format(
                               arrow.get(right_value.value).format('YYYY-MM-DD HH:mm:ss')
                           ))
            else:
                return operator_, left_value, right_value

    def _build_criterion_expression(self, operator_: str, left: Term, right: Term) -> Union[BasicCriterion,
                                                                                            Not,
                                                                                            NullCriterion]:
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
