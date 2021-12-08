from datetime import datetime
from typing import List

from model.model.topic.topic import Topic

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import is_not_raw
from watchmen.analysis.model.factor_index import FactorIndex
from watchmen.analysis.storage import factor_index_storage


def create_factor_index_data(topic: Topic, current_user) -> List[FactorIndex]:
    if is_not_raw(topic):
        for factor in topic.factors:
            factor_index = build_factor_index(factor, topic)
            factor_index_storage.create_factor_index_to_storage(factor_index)


def build_factor_index(factor, topic):
    factor_index = FactorIndex()
    factor_index.factorIndexId = get_surrogate_key()
    factor_index.type = factor.type
    factor_index.factorId = factor.factorId
    factor_index.tenantId = topic.tenantId
    factor_index.name = factor.name
    factor_index.label = factor.label
    factor_index.topicId = topic.topicId
    factor_index.topicName = topic.name
    factor_index.description = factor.description
    factor_index.createTime = datetime.now().replace(tzinfo=None).isoformat()
    return factor_index


def __build_factor_index_key(factor_id, topic_id):
    return factor_id + "_" + topic_id


def update_factor_index_data(topic: Topic, tenantId: str):
    if is_not_raw(topic):
        factor_index_list = factor_index_storage.load_factor_index_by_topic(topic.topicId, tenantId)
        db_factor_index_dict = {}
        new_factor_index_dict = {}
        for factor_index in factor_index_list:
            u_key = __build_factor_index_key(factor_index.factorId, factor_index.topicId)
            db_factor_index_dict[u_key] = factor_index

        for factor in topic.factors:
            u_key = __build_factor_index_key(factor.factorId, topic.topicId)
            new_factor_index_dict[u_key] = build_factor_index(factor, topic)

        for key, factor_index in db_factor_index_dict.items():
            if key not in new_factor_index_dict:
                factor_index_storage.delete_factor_index(factor_index)

        for key, factor_index in new_factor_index_dict.items():
            if key in db_factor_index_dict:
                factor_index_storage.update_factor_index_to_storage(factor_index)
            else:
                factor_index_storage.create_factor_index_to_storage(factor_index)
