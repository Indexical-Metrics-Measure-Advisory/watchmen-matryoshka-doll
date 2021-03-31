from watchmen.common.storage.engine_adaptor import find_template
from watchmen.common.utils.data_utils import build_collection_name

template = find_template()


def query_pipeline_monitor(topic_name, query, pagination):
    return template.query_with_pagination(collection_name=build_collection_name(topic_name), pagination=pagination,
                                          query_dict=query)
