from watchmen.database.topic.adapter.topic_storage_adapter import get_template_by_datasource_id
from watchmen.topic.storage.topic_schema_storage import get_topic_by_name


def query_pipeline_monitor(topic_name, query, pagination):
    topic = get_topic_by_name(topic_name)
    storage_template = get_template_by_datasource_id(topic.dataSourceId)
    result = storage_template.topic_data_page_(query, None, pagination, None, topic_name)
    return result
