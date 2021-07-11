from watchmen.database.storage.storage_template import topic_data_page_


# template = find_template()


def query_pipeline_monitor(topic_name, query, pagination):
    result = topic_data_page_(query, None, pagination, None, topic_name)
    return result
