
import json


def batch_load():
    pass


def row_data_load(path: str):
    with open(path) as f:
        return  json.loads(f.read())
        #





