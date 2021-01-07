from watchmen.common.mongo.index import check_collection_if_exist
from watchmen.pipeline.single.constants import TOPIC, TOPIC_TYPE
from watchmen.pipeline.single.filter.filter_data import filter_data


def __generate_sql(request):
    return ""


def find_data(sql):
    pass


def create_new_collection(collection_name, data_rows):
    return None


def init(**kwargs):
    factors = kwargs["factors"]
    dimensions = kwargs["dimensions"]
    topic_name = kwargs[TOPIC]
    topic_type = kwargs[TOPIC_TYPE]

    def aggregate_factors(request):
        filter_result = filter_data(request)
        collection_name = build_collection_name(topic_name, topic_type, dimensions)
        if check_collection_if_exist(None, collection_name):

            # load current dimensions and update data
            pass
        else:
            # load data from sql
            sql = __generate_sql(request)
            data_rows = find_data(sql)
            # error handling

            result = create_new_collection(collection_name, data_rows)

            # create new aggregate topic

            # send notifications
            return result

        return request

    return aggregate_factors


def build_collection_name(topic_name, topic_type, dimensions):
    base_name = topic_type + "_" + topic_name
    for dimension in dimensions:
        base_name = base_name + "_" + dimension

    return base_name[:-1]
