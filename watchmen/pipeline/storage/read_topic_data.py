from watchmen.database.topic.adapter.topic_storage_adapter import get_template_by_datasource_id
from watchmen.topic.topic import Topic


def query_topic_data(where_, topic: Topic):
    template = get_template_by_datasource_id(topic.dataSourceId)
    return template.topic_data_find_one(where_, topic.name)


def query_multiple_topic_data(where_, topic: Topic):
    template = get_template_by_datasource_id(topic.dataSourceId)
    return template.topic_data_find_(where_, topic.name)


def query_topic_data_aggregate(where, aggregate, topic: Topic):
    template = get_template_by_datasource_id(topic.dataSourceId)
    return template.topic_data_find_with_aggregate(where, topic.name, aggregate)
