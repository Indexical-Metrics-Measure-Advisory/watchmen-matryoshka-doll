
from watchmen.pipeline.single.constants import TOPIC
from watchmen.topic.storage import save_topic_instance, get_topic_instances


MERGE_KEY = "merge_key"


def find_key_in_storage(topic_name, merge_key, key_value):
    return get_topic_instances(topic_name,{merge_key:key_value})


# def merge_data(data, storage_data):
#     return storage_data


def save_to_topic(result, topic_name):
    return save_topic_instance(topic_name,result)


def init(**kwargs):
    # if MERGE_KEY in kwargs:
        # merge_key = kwargs[MERGE_KEY]
    topic_name = kwargs[TOPIC]

    def insert_topic(raw_data):
        if type(raw_data) is list:
            for data in raw_data:
                print(data)
                return save_to_topic(data, topic_name)
                    # if merge_key in data:
                        # key_value = data[merge_key]
                        # print("merge_key",merge_key)
                        # print("key_value", key_value)
                        # storage_data = find_key_in_storage(topic_name, merge_key, key_value)
                        # result = merge_data(data, storage_data)

    return insert_topic



def trigger(**kwargs) -> bool:
    return True
