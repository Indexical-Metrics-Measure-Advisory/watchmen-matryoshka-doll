from watchmen.space.storage.space_storage import get_space_by_id
from watchmen.topic.storage.topic_schema_storage import get_topic_list_by_ids


def load_topic_list_by_space_id(space_id, current_user):
    space = get_space_by_id(space_id, current_user)
    if space.topicIds is None:
        return []
    else:
        return get_topic_list_by_ids(space.topicIds, current_user)
