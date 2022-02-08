from typing import List
from watchmen.parser.parameter import ParameterJoint

from model.model.space.space import SpaceFilter


from watchmen.console_space.storage.console_space_storage import load_console_space_by_subject_id
from watchmen.parser.console_paramter_parser import ConsoleParameterJointParser
from watchmen.report.builder.dialects import PrestoQuery
from watchmen.report.builder.utils import build_table_by_topic_id
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


def build_space_filter_where(filter_: ParameterJoint):
    parser_ = ConsoleParameterJointParser(filter_)
    return parser_.parse_parameter_joint()
