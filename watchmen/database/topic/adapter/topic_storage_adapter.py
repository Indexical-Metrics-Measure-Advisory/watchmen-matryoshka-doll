from watchmen.database.datasource.container import data_source_container
from watchmen.database.topic.topic_storage_template import TopicStorageEngine



def get_template_by_datasource_id(datasource_id):
    template = TopicStorageEngine(data_source_container.get_storage(datasource_id))
    return template








