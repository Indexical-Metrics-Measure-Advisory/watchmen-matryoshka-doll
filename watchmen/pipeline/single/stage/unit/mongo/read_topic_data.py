from watchmen.common.storage.storage_template import topic_data_find_one, topic_data_find_


# db = get_client()


def query_topic_data(where_, topic_name):
    """
    codec_options = build_code_options()
    collection_name = build_collection_name(topic_name)
    collection = db.get_collection(collection_name, codec_options=codec_options)
    result = collection.find_one(mongo_query)
    return result
    """
    return topic_data_find_one(where_, topic_name)


def query_multiple_topic_data(where_, topic_name):
    return topic_data_find_(where_, topic_name)
