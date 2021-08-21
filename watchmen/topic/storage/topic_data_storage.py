from watchmen.common.utils.data_utils import add_tenant_id_to_instance
from watchmen.database.topic.adapter.topic_storage_adapter import get_template_by_datasource_id
from watchmen.topic.topic import Topic


def save_topic_instance(topic: Topic, instance,current_user=None):
    template = get_template_by_datasource_id(topic.dataSourceId)
    return template.topic_data_insert_one(add_tenant_id_to_instance(instance,current_user), topic.name)


def save_topic_instances(topic: Topic, instances):
    template = get_template_by_datasource_id(topic.dataSourceId)
    return template.topic_data_insert_(instances, topic.name)


def update_topic_instance(topic: Topic, instance, instance_id):
    template = get_template_by_datasource_id(topic.dataSourceId)
    return template.topic_data_update_one(instance_id, instance, topic.name)


def get_topic_instances(topic: Topic, conditions):
    template = get_template_by_datasource_id(topic.dataSourceId)
    return template.topic_data_find_(conditions, topic.name)


def get_topic_instances_all(topic: Topic):
    template = get_template_by_datasource_id(topic.dataSourceId)
    return template.topic_data_list_all(topic.name)


def find_topic_data_by_id_and_topic_name(topic: Topic, object_id) -> Topic:
    template = get_template_by_datasource_id(topic.dataSourceId)
    return template.topic_data_find_by_id(object_id, topic.name)
