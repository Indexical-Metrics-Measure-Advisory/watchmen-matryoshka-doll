from bson import ObjectId

from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name

client = get_client()


# print("save_topic_instance",client)


# @topic_event_trigger
def save_topic_instance(topic_name, instance):
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    topic_instance_col.insert(instance)
    return topic_name, instance


def save_topic_instances(topic_name, instances):
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    topic_instance_col.insert_many(instances)


def get_topic_instances(topic_name, conditions):
    # print(topic_name)
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    return topic_instance_col.find(conditions)


def find_topic_data_by_id_and_topic_name(topic_name, object_id):
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    return find_topic_data_by_id(topic_instance_col, ObjectId(object_id))


def find_topic_data_by_id(collection, id):
    result = collection.find_one({"_id": id})
    return result
