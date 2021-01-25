import importlib
import logging
import traceback
from datetime import datetime

from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus
from watchmen.monitor.storage.pipeline_monitor_storage import insert_pipeline_monitor
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

NAME = "name"

PARAMETER = "parameter"

STAGE_MODULE_PATH = 'watchmen.pipeline.single.stage.unit.action.'

log = logging.getLogger("app." + __name__)


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
    pipeline_status = PipelineRunStatus()
    pipeline_status.topicId = pipeline.topicId
    pipeline_status.pipelineId = pipeline.pipelineId
    pipeline_status.uid = get_surrogate_key()
    pipeline_topic = get_topic_by_id(pipeline.topicId)

    try:
        start_time = datetime.now()

        # time.time
        for stage in pipeline.stages:
            for unit in stage.units:
                if unit.on is not None:
                    pass  # TODO check when condition
                actions = unit.do
                # out_result = None

                # print("len ", len(actions))
                for action in actions:
                    log.debug("action: {}".format(action.json()))
                    func = find_action_type_func(convert_action_type(action.type), action, pipeline_topic)
                    # print("func: ", func)
                    out_result = func(data)

        # TODO create pipeline status topic
        # TODO set max limit for monitor topic

        time_elapsed = datetime.now() - start_time
        execution_time = time_elapsed.microseconds / 1000
        pipeline_status.complete_time = execution_time
        pipeline_status.status = "FINISHED"

        log.info("pipeline_status {0} time :{1}".format(pipeline.name, execution_time))

    except Exception as e:
        log.error(e)
        pipeline_status.error = traceback.format_exc()
        pipeline_status.status = "ERROR"
    finally:
        # log.info("insert_pipeline_monitor")
        insert_pipeline_monitor(pipeline_status)

    # return data
