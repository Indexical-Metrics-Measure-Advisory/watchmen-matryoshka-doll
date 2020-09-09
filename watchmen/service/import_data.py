import json

from lib.model.model_schema import ModelSchema


class Event(object):
    code:str
    type:str



def import_row_data(data:json,schema:ModelSchema,event:Event):
    # find root
    # build relationship




    # find schema

    # extract data topic base on schema



    pass


def batch_import_data():
    # find schema

    # extract data topic base on schema

    # TODO use dark for parallel run
    pass
