import importlib
from datetime import datetime

from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

NAME = "name"

PARAMETER = "parameter"

STAGE_MODULE_PATH = 'watchmen.pipeline.single.stage.unit.action.'


def build_pipeline(stage_list):
    pipeline = []
    for stage_config in stage_list:
        stage_method = importlib.import_module(STAGE_MODULE_PATH + stage_config[NAME])
        stage = stage_method.init(**stage_config[PARAMETER])
        pipeline.append(stage)
    return pipeline


def find_action_type_func(action_type, action, pipeline_topic):
    stage_method = importlib.import_module(STAGE_MODULE_PATH + action_type)
    return stage_method.init(action, pipeline_topic)


def convert_action_type(action_type: str):
    return action_type.replace("-", "_")


def run_pipeline(pipeline, data):
    pipeline_type = pipeline.type
    pipeline_topic = get_topic_by_id(pipeline.topicId)

    # run_status = PipelineRunStatus()
    # run_status.status = run_status.status

    # run_status.name = pipeline.name
    # now =datetime.now()

    start_time = datetime.now()

    # time.time
    for stage in pipeline.stages:
        for unit in stage.units:
            if unit.on is not None:
                pass  # TODO check when condition
            actions = unit.do
            # out_result = None

            print("len ", len(actions))
            for action in actions:
                print("action: ", action.json())
                func = find_action_type_func(convert_action_type(action.type), action, pipeline_topic)
                print("func: ", func)
                out_result = func(data)

    # TODO create pipeline status topic
    # TODO set max limit for monitor topic

    time_elapsed = datetime.now() - start_time

    print('Time elapsed ', time_elapsed.microseconds / 1000)

    return data
    # parent_node = None
    # for stage in pipeline:
    #     if parent_node is None:
    #         parent_node = dask.delayed(stage)(data)
    #     else:
    #         parent_node = dask.delayed(stage)(parent_node)
    # parent_node.compute()
