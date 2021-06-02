from typing import List

# from storage.storage import
from storage.storage.storage_template import topic_data_insert_one, topic_data_insert_, topic_data_update_one, \
     topic_data_find_, topic_data_list_all, topic_data_find_by_id

from watchmen.topic.topic import Topic


# topic_data_insert_one
# client = get_client()


# print("save_topic_instance",client)


# @topic_event_trigger
def save_topic_instance(topic_name, instance):
    '''
    codec_options = build_code_options()
    topic_instance_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
    topic_instance_col.insert(instance)
    return topic_name, instance
    '''
    return topic_data_insert_one(instance, topic_name)


def save_topic_instances(topic_name, instances):
    """
    codec_options = build_code_options()
    topic_instance_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
    topic_instance_col.insert_many(instances)
    """
    return topic_data_insert_(instances, topic_name)


def update_topic_instance(topic_name, instance, instance_id):
    """
    codec_options = build_code_options()
    topic_instance_col = client.get_collection(build_collection_name(topic_name), codec_options=codec_options)
    topic_instance_col.update_one({"_id": ObjectId(instance_id)}, {"$set": instance})
    """
    return topic_data_update_one(instance_id, instance, topic_name)


def get_topic_instances(topic_name, conditions):
    '''
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    return topic_instance_col.find(conditions)
    '''
    return topic_data_find_(conditions, topic_name)


def get_topic_instances_all(topic_name) -> List[Topic]:
    """
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    result = topic_instance_col.find()
    return list(result)
    """
    return topic_data_list_all(topic_name)


def find_topic_data_by_id_and_topic_name(topic_name, object_id) -> Topic:
    '''
    topic_instance_col = client.get_collection(build_collection_name(topic_name))
    return find_topic_data_by_id(topic_instance_col, ObjectId(object_id))
    '''
    return topic_data_find_by_id(object_id, topic_name)


'''
def find_topic_data_by_id(collection, id):
    result = collection.find_one({"_id": id})
    return result
'''
