import logging
from typing import List

from watchmen.auth.storage.user_group import USER_GROUPS
from watchmen.auth.user import User
from watchmen.auth.user_group import UserGroup
from watchmen.common.data_page import DataPage
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.database.storage.storage_template import find_
from watchmen.raw_data.model_schema import ModelSchema
from watchmen.raw_data.model_schema_set import ModelSchemaSet
from watchmen.space.space import Space
from watchmen.space.storage.space_storage import SPACES
from watchmen.topic.factor.factor import Factor
from watchmen.topic.storage.topic_schema_storage import save_topic, update_topic
from watchmen.topic.topic import Topic

log = logging.getLogger("app." + __name__)


class QueryTopic(Topic):
    factorCount: int = 0
    reportCount: int = 0
    groupCount: int = 0
    spaceCount: int = 0


def create_topic_schema(topic: Topic) -> Topic:
    if topic.topicId is None or check_fake_id(topic.topicId):
        topic.topicId = get_surrogate_key()
    '''   
    if type(topic) is not dict:
        topic = topic.dict()
    '''
    save_topic(topic)
    return Topic.parse_obj(topic)


def update_topic_schema(
        topic_id,
        topic: Topic):
    '''
    if type(topic) is not dict:
        topic = topic.dict()
    '''
    update_topic(topic_id, topic)
    return Topic.parse_obj(topic)


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
    return find_(where, Space, SPACES)


def __find_groups_in_topic_id(topic_id, current_user):
    where = {"and": [{"topicIds": {"in": [topic_id]}}, {"tenantId": current_user.tenantId}], }
    return find_(where, UserGroup, USER_GROUPS)
