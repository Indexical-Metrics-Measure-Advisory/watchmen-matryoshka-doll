from storage.storage.storage_template import topic_data_page_


# template = find_template()


def query_pipeline_monitor(topic_name, query, pagination):

    print(topic_name)

    print(pagination)
    """
    return template.query_with_pagination(collection_name=build_collection_name(topic_name), pagination=pagination,
                                          query_dict=query)
    """
    '''
    return page_(query, None, pagination, None, topic_name)
    '''
    return topic_data_page_(query, None, pagination, None, topic_name)
