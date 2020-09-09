import json

from watchmen.schema.model_schema import ModelSchema


class Event(object):
    code:str
    type:str


def process_topic_data():
    pass


def process_data_attr():
    pass



def import_row_data(data:json,schema:ModelSchema,event:Event):
    for key, value in data.items():






        # find sub schema in relationship schema
        # process attr
        # generate ID   for sub schema`s relationship
        #

        pass



    # find root
    # build relationship





    # find schema

    # extract data topic base on schema



    pass


def batch_import_data():
    # find schema

    # extract data topic base on schema

    # TODO[future] use dark for parallel run
    pass
