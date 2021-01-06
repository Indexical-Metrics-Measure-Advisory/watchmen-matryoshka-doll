
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import WATCHMEN

client = get_client(WATCHMEN)


# def update_topic_instance(topic_name,data):
#     pass


def build_collection_name(topic_name):
    return "topic_"+topic_name


def save_topic_instance(topic_name, instance):
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    topic_instance_col.insert_one(instance)


def save_topic_instances(topic_name, instances):
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    topic_instance_col.insert_many(instances)


def get_topic_instances(topic_name, conditions):
    print(topic_name)
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    return topic_instance_col.find(conditions)
