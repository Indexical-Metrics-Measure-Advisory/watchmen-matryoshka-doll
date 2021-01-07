from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.space.space import Space
from watchmen.space.storage.space_storage import insert_space_to_storage, load_space_by_name, update_space_to_storage
from watchmen.topic.topic import Topic


def create_space(space: Space):
    if type(space) is not dict:
        space = space.dict()
    space["spaceId"] = get_surrogate_key()
    return insert_space_to_storage(space).inserted_id


def update_space_by_id(space_id: int, space: Space):
    if type(space) is not dict:
        space = space.dict()
    update_space_to_storage(space_id, space)
    return space


def load_space(name: str):
    return load_space_by_name(name)


def add_topic_to_space(topic: Topic, space: Space):
    topic_list = space.topic_list
    if topic_list is None:
        topic_list = []
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


def update_topic_in_space(topic: Topic, space: Space):
    topic_list = __merge_topic_list(space.topic_list, topic)
    space.topic_list = topic_list
    return update_space_to_storage(space)
