from watchmen.topic.storage.topic_schema_storage import get_topic_by_id


def test_load_topic_by_id():
    topic_id = 797062163784007680
    get_topic_by_id(topic_id)
