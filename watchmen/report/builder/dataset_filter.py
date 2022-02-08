from typing import List
from model.model.common.parameter import ParameterJoint
from model.model.report.column import Column
from pypika import Field
from watchmen.parser.console_paramter_parser import ConsoleParameterParser, ConsoleParameterJointParser


def build_dataset_select_fields(columns: List[Column], topic_space_filter) -> List[Field]:
    fields = []
    for column in columns:
        parameter = column.parameter
        parser = ConsoleParameterParser(parameter, topic_space_filter)
        parser_result = parser.parse_parameter()
        fields.append(parser_result.result.as_(column.alias))
    return fields


def build_dataset_where(filter_: ParameterJoint, topic_space_filter):
    parser_ = ConsoleParameterJointParser(filter_, topic_space_filter)
    return parser_.parse_parameter_joint()

