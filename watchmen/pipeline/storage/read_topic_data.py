from watchmen.database.storage.storage_template import topic_data_find_one, topic_data_find_, \
    topic_data_find_with_aggregate


def query_topic_data(where_, topic_name):
    return topic_data_find_one(where_, topic_name)


def query_multiple_topic_data(where_, topic_name):
    return topic_data_find_(where_, topic_name)


def query_topic_data_aggregate(where, topic_name, aggregate):
    return topic_data_find_with_aggregate(where, topic_name, aggregate)
