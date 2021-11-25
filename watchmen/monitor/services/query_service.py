from watchmen.database.topic.adapter.topic_storage_adapter import get_template_by_datasource_id
from watchmen.monitor.services.pipeline_monitor_service import find_monitor_topic


def query_pipeline_monitor(topic_name, query, pagination, current_user=None):
    topic = find_monitor_topic(topic_name, current_user)
    storage_template = get_template_by_datasource_id(topic.dataSourceId)
    result = storage_template.topic_data_page_(query, None, pagination, None, topic_name)
    return result
