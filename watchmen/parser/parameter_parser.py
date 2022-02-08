from abc import abstractmethod
from typing import Union, Tuple, Any

from model.model.common.parameter import Parameter
from pypika import Field
from pypika.terms import CustomFunction, ArithmeticExpression, Function

from watchmen.parser.constants import ParameterKind, ParameterValueType
from watchmen.parser.parameter import ParameterJoint


class ParseResult:
    def __init__(self, result: Union[Field, CustomFunction, ArithmeticExpression], value_type: ParameterValueType):
        self.result = result
        self.value_type = value_type


class ParameterParser:

    def __init__(self, param: Parameter):
        self.param = param

    def parse_parameter(self) -> ParseResult:
        if self.param.kind == ParameterKind.TOPIC:
            result, value_type = self.topic_handle()
            return ParseResult(result, value_type)
        elif self.param.kind == ParameterKind.CONSTANT:
            result, value_type = self.constant_handle()
            return ParseResult(result, value_type)
        elif self.param.kind == ParameterKind.COMPUTED:
            result, value_type = self.computed_handle()
            return ParseResult(result, value_type)

    @abstractmethod
    def topic_handle(self) -> Tuple[Union[Field, CustomFunction],
                                    ParameterValueType]:
        pass

    @abstractmethod
    def constant_handle(self) -> Tuple[CustomFunction, ParameterValueType]:
        pass

    @abstractmethod
    def computed_handle(self) -> Tuple[Union[ArithmeticExpression, Function],
                                       ParameterValueType]:
        pass


class ParameterJointParser:

    def __init__(self, parameter_joint: ParameterJoint):
        self.parameter_joint = parameter_joint

    def parse_parameter_joint(self) -> Any:
        if self.parameter_joint.jointType:
            return self.parse_joint()
        else:
            return self.parse_criterion()

    @abstractmethod
    def parse_joint(self) -> Any:
        pass

    @abstractmethod
    def parse_criterion(self) -> Any:
        pass

    @abstractmethod
    def type_inference(self, operator_, left: ParseResult, right: ParseResult) -> Tuple[Any, Any]:
        pass

    @abstractmethod
    def _build_criterion_expression(self, operator_: str, left: Any, right: Any) -> Any:
        pass
