from watchmen.database.topic.adapter.topic_storage_adapter import get_template_by_datasource_id
from watchmen.monitor.services.pipeline_monitor_service import find_monitor_topic
from watchmen.topic.storage.topic_schema_storage import get_topic_by_name


def query_pipeline_monitor(topic_name, query, pagination, current_user=None):
    topic = find_monitor_topic(topic_name, current_user)
    storage_template = get_template_by_datasource_id(topic.dataSourceId)
    result = storage_template.topic_data_page_(query, None, pagination, None, topic_name)
    return result


# def find_monitor_topic(topic_name, current_user):
#     topic = get_topic_by_name(topic_name, current_user)
#     if topic is None:
#         return get_topic_by_name(topic_name)
#     else:
#         return topic
