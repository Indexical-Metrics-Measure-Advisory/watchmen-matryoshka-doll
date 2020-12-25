from pandas import DataFrame

from watchmen.pipeline.single.filter.filter_data import filter_data


def run_mapping_rules(mapping_rules, filter_result:DataFrame):
    topics=[]
    for row_data in filter_result.values:
        topic={}
        for i in range(len(row_data)):
            topic[filter_result.columns[i]]=row_data[i]

        topics.append(topic)
    return topics


def init(**kwargs):
    mapping_rules = kwargs["mapping_rules"]



    def mapping_to_topic(request):
        ## convert data to
        filter_result= filter_data(request)
        return run_mapping_rules(mapping_rules,filter_result)

    return mapping_to_topic



