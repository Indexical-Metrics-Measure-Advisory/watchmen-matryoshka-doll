from watchmen.topic.storage.topic_schema_storage import get_topic_by_id, save_topic


def test_load_topic_by_id():
    topic_id = "801388424895397888"

    save_topic(get_topic_by_id(topic_id).dict())
    # for i in range(20):
    #     get_topic_by_id(topic_id)
    # get_topic_by_id(topic_id)
    # get_topic_by_id(topic_id)
    # get_topic_by_id(topic_id)
