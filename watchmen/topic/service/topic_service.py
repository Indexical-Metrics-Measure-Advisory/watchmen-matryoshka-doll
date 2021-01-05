from watchmen.topic.storage.topic_schema_storage import save_topic, get_topic_list_like_topic_name, get_topic_by_id
from watchmen.topic.topic import Topic


def create_topic_schema(topic:Topic):
    insert_topic = save_topic(topic)
    insert_topic.inserted_id


    return


def update_topic_schema(topic_id,topic:Topic):
    topic = get_topic_by_id(topic_id)
    if topic is not None:
        pass

    pass


def query_topic_schema(query_name:str):
    return get_topic_list_like_topic_name(query_name)








