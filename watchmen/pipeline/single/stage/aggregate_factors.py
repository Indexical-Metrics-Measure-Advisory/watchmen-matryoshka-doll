from watchmen.common.mongo.index import check_collection_if_exist
from watchmen.pipeline.single.constants import TOPIC,TOPIC_TYPE


def init(**kwargs):
    factors = kwargs["factors"]
    dimensions = kwargs["dimensions"]
    topic_name = kwargs[TOPIC]
    topic_type = kwargs[TOPIC_TYPE]

    def filter_data(data):
        return data

    def aggregate_factors(request):
        filter_result = filter_data(request)
        collection_name = build_collection_name(topic_name,topic_type,dimensions)
        if check_collection_if_exist(None,collection_name):
            # load current dimensions and update data
            pass
        else:
            # load data from sql
            # create new aggregate topic
            # update data
            # send notifications
            pass







        ## check wether exsiting collection



        ## generate sql base on request conditions
        ## call presto clinet get aggregate_factors
        ## insert data


        ## convert data to

        return request

    return aggregate_factors


def build_collection_name(topic_name,topic_type,dimensions):
    base_name = topic_type+"_"+topic_name
    for dimension in dimensions:
        base_name = base_name+"_"+dimension

    return base_name[:-1]