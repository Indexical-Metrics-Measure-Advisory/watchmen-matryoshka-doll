import pandas

from watchmen.pipeline.stage_constants import SPILT_FACTOR, SPILT_FACTOR_VALUE, DATA, FILTER
from watchmen.raw_data.entity.data_entity_set import DataEntitySet


def init(**kwargs):
    factor_name = kwargs[SPILT_FACTOR]
    factor_name_value = kwargs[SPILT_FACTOR_VALUE]
    filter_factor = kwargs[FILTER]

    def filter_data(raw_data: DataEntitySet):

        for data_entity in raw_data.entities:
            if data_entity.topicCode == filter_factor:
                return data_entity

    def split_topic_by_schema(request):
        raw_data = request[DATA]
        filter_result = filter_data(raw_data)
        d = filter_result.attr
        pandas_dict = convert_dict_to_pandas_dict(filter_result.attr)
        df = pandas.DataFrame.from_dict(pandas_dict)
        return df[df[factor_name] == factor_name_value]
    return split_topic_by_schema


# def trigger(**kwargs) -> bool:
#     pass

def get_name():
    return "split data by topic name"

def convert_dict_to_pandas_dict(kv):
    new_kv={}
    for k,v in kv.items():
        new_kv[k]=[v]
    return new_kv
