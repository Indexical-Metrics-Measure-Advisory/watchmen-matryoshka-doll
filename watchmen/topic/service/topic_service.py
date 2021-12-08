import logging
from typing import List

from model.model.common.data_page import DataPage
from model.model.common.user import User
from model.model.space.space import Space
from model.model.topic.factor import Factor
from model.model.topic.topic import Topic

from watchmen.auth.storage.user_group import USER_GROUPS
from watchmen.auth.user_group import UserGroup
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.config.config import settings
from watchmen.database.find_storage_template import find_storage_template
from watchmen.raw_data.model_schema import ModelSchema
from watchmen.raw_data.model_schema_set import ModelSchemaSet
from watchmen.space.storage.space_storage import SPACES
from watchmen.analysis.service import factor_index_service
from watchmen.topic.storage.topic_schema_storage import save_topic, update_topic

log = logging.getLogger("app." + __name__)

storage_template = find_storage_template()


class QueryTopic(Topic):
    factorCount: int = 0
    reportCount: int = 0
    groupCount: int = 0
    spaceCount: int = 0


def create_topic_schema(topic: Topic) -> Topic:
    if topic.topicId is None or check_fake_id(topic.topicId):
        topic.topicId = get_surrogate_key()
    save_topic(topic)
    result = Topic.parse_obj(topic)
    if settings.FACTOR_INDEX_ON:
        factor_index_service.create_factor_index_data(result, topic.tenantId)
    return result


def update_topic_schema(
        topic_id,
        topic: Topic):
    update_topic(topic_id, topic)
    result = Topic.parse_obj(topic)
    if settings.FACTOR_INDEX_ON:
        factor_index_service.update_factor_index_data(result, topic.tenantId)
    return result


def build_topic(model_schema_set: ModelSchemaSet, current_user):
    topic = Topic()
    topic.tenantId = current_user.tenantId
    topic.topicId = get_surrogate_key()
    topic.name = model_schema_set.code
    topic.type = "raw"
    topic.factors = []
    parent = ""
    build_factors(topic.factors, parent, model_schema_set.schemas[topic.name], model_schema_set)
    create_topic_schema(topic)


def build_factors(factors: list, parent: str, model_schema: ModelSchema, model_schema_set: ModelSchemaSet):
    for key, value in model_schema.businessFields.items():
        if value.type == "array" or value.type == "dict":
            factor = Factor()
            if parent == "":
                factor.name = key
                factor.label = key
                build_factors(factors, key, model_schema_set.schemas[key], model_schema_set)
            else:
                factor.name = parent + "." + key
                factor.label = parent + "." + key
                build_factors(factors, parent + "." + key, model_schema_set.schemas[key], model_schema_set)
            factor.type = value.type
            factor.factorId = get_surrogate_key()
            factors.append(factor)
        else:
            factor = Factor()
            if parent != "":
                factor.name = parent + "." + key
                factor.label = parent + "." + key
            else:
                factor.name = key
                factor.label = key
            factor.type = value.type
            factor.factorId = get_surrogate_key()
            factors.append(factor)


def merge_summary_data_for_topic(data_page: DataPage, current_user: User):
    topic_list: List[Topic] = data_page.data
    if topic_list:
        query_topic_list = []
        for topic in topic_list:
            query_topic = QueryTopic.parse_obj(topic)
            query_topic.factorCount = len(topic.factors)
            query_topic.spaceCount = len(__find_spaces_in_topic_id(topic.topicId, current_user))
            query_topic_list.append(query_topic)
        data_page.data = query_topic_list


def __find_spaces_in_topic_id(topic_id, current_user):
    where = {"and": [{"topicIds": {"in": [topic_id]}}, {"tenantId": current_user.tenantId}], }
    return storage_template.find_(where, Space, SPACES)


def __find_groups_in_topic_id(topic_id, current_user):
    where = {"and": [{"topicIds": {"in": [topic_id]}}, {"tenantId": current_user.tenantId}], }
    return storage_template.find_(where, UserGroup, USER_GROUPS)
