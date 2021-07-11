from watchmen.database.storage.storage_template import topic_data_insert_one, topic_data_insert_, topic_data_update_one, \
    topic_data_find_, topic_data_list_all, topic_data_find_by_id
from watchmen.topic.topic import Topic


def save_topic_instance(topic_name, instance):
    return topic_data_insert_one(instance, topic_name)


def save_topic_instances(topic_name, instances):
    return topic_data_insert_(instances, topic_name)


def update_topic_instance(topic_name, instance, instance_id):
    return topic_data_update_one(instance_id, instance, topic_name)


def get_topic_instances(topic_name, conditions):
    return topic_data_find_(conditions, topic_name)


def get_topic_instances_all(topic_name):
    return topic_data_list_all(topic_name)


def find_topic_data_by_id_and_topic_name(topic_name, object_id) -> Topic:
    return topic_data_find_by_id(object_id, topic_name)

