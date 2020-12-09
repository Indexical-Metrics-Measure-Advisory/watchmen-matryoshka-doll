

from watchmen.pipeline.stage_constants import SPILT_FACTOR


def init(**kwargs):
    # if schema is empty ,generate a raw schema
    # split data base on schema
    # return topic_list , relationship and schema
    factor_name = kwargs[SPILT_FACTOR]

    def run(raw_data):

        pass

        # if type(raw_data) is not dict:
        #     pass # error
        # else:
        #     data_frames = pandas.DataFrame.from_dict()
        #     data = data_frames.groupby([factor_name])
        #     print(data)
        #     return data

    return run


def trigger(**kwargs) -> bool:

    pass
