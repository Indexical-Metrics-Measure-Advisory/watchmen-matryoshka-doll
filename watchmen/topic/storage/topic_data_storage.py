from bson import ObjectId

from watchmen.common.mongo.index import build_code_options
from watchmen.common.storage.engine.storage_engine import get_client
from watchmen.common.utils.data_utils import build_collection_name

client = get_client()


# print("save_topic_instance",client)


# @topic_event_trigger
def save_topic_instance(topic_name, instance):
    codec_options = build_code_options()
    topic_instance_col = client.get_collection(build_collection_name(topic_name),codec_options=codec_options)
    topic_instance_col.insert(instance)
    return topic_name, instance


def save_topic_instances(topic_name, instances):
    codec_options = build_code_options()
    topic_instance_col = client.get_collection(build_collection_name(topic_name),codec_options=codec_options)
    topic_instance_col.insert_many(instances)


def update_topic_instance(topic_name, instance, instance_id):
    codec_options = build_code_options()
    topic_instance_col = client.get_collection(build_collection_name(topic_name),codec_options=codec_options)
    topic_instance_col.update_one({"_id": ObjectId(instance_id)}, {"$set": instance})


def get_topic_instances(topic_name, conditions):
    # print(topic_name)
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    return topic_instance_col.find(conditions)


def get_topic_instances_all(topic_name):
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    result = topic_instance_col.find()
    return list(result)


def find_topic_data_by_id_and_topic_name(topic_name, object_id):
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    return find_topic_data_by_id(topic_instance_col, ObjectId(object_id))


def find_topic_data_by_id(collection, id):
    result = collection.find_one({"_id": id})
    return result
