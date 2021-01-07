import importlib

import dask

NAME = "name"

PARAMETER = "parameter"

STAGE_MODULE_PATH = 'watchmen.pipeline.single.stage.'


def build_pipeline(stage_list):
    pipeline = []
    for stage_config in stage_list:
        stage_method = importlib.import_module(STAGE_MODULE_PATH + stage_config[NAME])
        stage = stage_method.init(**stage_config[PARAMETER])
        pipeline.append(stage)
    return pipeline


def run_pipeline(pipeline, data):
    parent_node = None
    for stage in pipeline:
        if parent_node is None:
            parent_node = dask.delayed(stage)(data)
        else:
            parent_node = dask.delayed(stage)(parent_node)
    # parent_node.visualize(filename='transpose.svg',optimize_graph=True)
    parent_node.compute()
