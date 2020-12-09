from watchmen.space.topic.topic import Topic
from watchmen.space.space import Space
from watchmen.space.storage.space_storage import insert_space_to_storage, load_space_by_name, update_space_to_storage


def save_space(space: Space):
    return insert_space_to_storage(space)


def load_space(name: str):
    return load_space_by_name(name)


def add_topic_to_space(topic: Topic, space: Space):
    topic_list = space.topic_list
    if topic_list is None:
        topic_list =[]
    topic_list.append(topic)
    space.topic_list = topic_list
    return update_space_to_storage(space)


def __merge_topic_list(topic_list, topic):
    merge_topic_list = []
    for old_topic in topic_list:
        if topic.topicName == old_topic["topicName"]:
            merge_topic_list.append(topic)
        else:
            merge_topic_list.append(old_topic)
    return merge_topic_list


def update_topic_in_space(topic: Topic, space:Space):
    topic_list = __merge_topic_list(space.topic_list, topic)
    space.topic_list = topic_list
    return update_space_to_storage(space)






