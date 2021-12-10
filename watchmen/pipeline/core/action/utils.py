import logging

from model.model.common.user import User
from model.model.pipeline.trigger_data import TriggerData
from model.model.topic.topic import Topic

from watchmen.common.utils.data_utils import get_id_name_by_datasource
from watchmen.database.datasource.container import data_source_container
from watchmen.database.topic.adapter.topic_storage_adapter import get_template_by_datasource_id
from watchmen.pipeline.storage.read_topic_data import query_topic_data

log = logging.getLogger("app." + __name__)


def update_recovery_callback(mappings_results: dict, where_: dict, target_topic: Topic):
    log.error("The maximum number of retry times (3) is exceeded, retry failed. Do recovery, "
              "mappings_results: {0}, where: {1}, target_topic: {2}".format(mappings_results, where_, target_topic))
    target_data = query_topic_data(where_,
                                   target_topic.name)
    if target_data is not None:
        id_ = target_data.get(
            get_id_name_by_datasource(data_source_container.get_data_source_by_id(target_topic.dataSourceId)), None)
        if id_ is not None:
            template = get_template_by_datasource_id(target_topic.dataSourceId)
            template.topic_data_update_one(id_, mappings_results, target_topic.name)
            data = {**target_data, **mappings_results}
            return TriggerData(topicName=target_topic.name,
                               triggerType="Update",
                               data={"new": data, "old": target_data})
        else:
            raise RuntimeError(
                "when do update topic {0}, the id_ {1} should not be None".format(target_topic.name, id_))
    else:
        raise RuntimeError(
            "target topic {0} recovery failed. the record is not exist. where: {1}".format(target_topic.name, where_))


def update_retry_callback(mappings_results: dict, where_: dict, target_topic: Topic, current_user: User):
    target_data = query_topic_data(where_,
                                   target_topic, current_user)

    if target_data is not None:
        id_ = target_data.get(
            get_id_name_by_datasource(data_source_container.get_data_source_by_id(target_topic.dataSourceId)), None)
        version_ = target_data.get("version_", None)
        if id_ is not None and version_ is not None:
            mappings_results['version_'] = version_
            template = get_template_by_datasource_id(target_topic.dataSourceId)
            template.topic_data_update_one_with_version(id_, version_, mappings_results, target_topic.name)
            data = {**target_data, **mappings_results}
            return TriggerData(topicName=target_topic.name,
                               triggerType="Update",
                               data={"new": data, "old": target_data})
        else:
            raise RuntimeError(
                "when do update topic {0}, the id_ {1} and version_ {2} should not be None".format(target_topic.name,
                                                                                                   id_, version_))
    else:
        raise RuntimeError(
            "update topic {0} failed, the target record is not exist. where: {1}".format(target_topic.name, where_))
