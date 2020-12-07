
import importlib
import dask


def build_pipeline(stage_list):
    pipeline = []
    for stage_config in stage_list:
        stage_method = importlib.import_module('watchmen.pipeline.single.stage.'+stage_config["name"])
        stage = stage_method.init(**stage_config["parameter"])
        pipeline.append(stage)
    return pipeline


def run_pipeline(pipeline,data):
    parent_node = None
    for stage in pipeline:
        if parent_node is None:
            parent_node = dask.delayed(stage)(data)
        else:
            parent_node = dask.delayed(stage)(parent_node)

    parent_node.compute()







