import importlib
import logging
import time
import traceback
from functools import lru_cache

from watchmen.common.constants import pipeline_constants
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus
from watchmen.monitor.storage.pipeline_monitor_storage import insert_pipeline_monitor, insert_units_monitor
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.pipeline.single.stage.unit.utils import STAGE_MODULE_PATH, PIPELINE_UID, ERROR, FINISHED
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

log = logging.getLogger("app." + __name__)


@lru_cache(maxsize=16)
def load_action_python(action_type):
    return importlib.import_module(STAGE_MODULE_PATH + action_type)


def find_action_type_func(action_type, action, pipeline_topic):
    stage_method = importlib.import_module(STAGE_MODULE_PATH + action_type)
    return stage_method.init(action, pipeline_topic)


@lru_cache(maxsize=16)
def convert_action_type(action_type: str):
    return action_type.replace("-", "_")


def __check_when_condition(children, data):
    if len(children) > 1:
        # TODO and and or condition
        pass
    else:

        # TODO __check_when_condition
        condition = children[0]
        # if condition.operator == NOT_EMPTY:
        #     topic = get_topic_by_id(condition.left.topicId)
        #     factor = get_factor(condition.left.factorId, topic)
        #     # get_factor_value
        #     return factor.name not in data


def run_pipeline(pipeline: Pipeline, data):
    pipeline_status = PipelineRunStatus()
    pipeline_status.topicId = pipeline.topicId
    pipeline_status.pipelineId = pipeline.pipelineId
    pipeline_status.uid = get_surrogate_key()
    pipeline_status.rawId = data[pipeline_constants.NEW][pipeline_constants.ID]

    if pipeline.enabled:
        pipeline_topic = get_topic_by_id(pipeline.topicId)
        # TODO pipeline when  condition

        context = {PIPELINE_UID: pipeline_status.uid}
        unit_status_list = []

        try:
            start = time.time()
            for stage in pipeline.stages:
                log.info("stage name {0}".format(stage.name))
                for unit in stage.units:
                    # if unit.on is not None:
                    #     result = __check_when_condition(unit.on.children, data)
                    #     if result:
                    #         continue

                    if unit.do is not None:
                        for action in unit.do:
                            func = find_action_type_func(convert_action_type(action.type), action, pipeline_topic)
                            # call dynamic action in action folder
                            out_result, unit_status = func(data, context)
                            # print("unit_status",unit_status)
                            unit_status.stageName = stage.name
                            unit_status_list.append(unit_status.dict())
                            log.debug("out_result :{0}".format(out_result))
                            context = {**context, **out_result}
                    else:
                        log.info("action stage unit  {0} do is None".format(stage.name))

            elapsed_time = time.time() - start
            pipeline_status.complete_time = elapsed_time
            pipeline_status.status = FINISHED
            log.info("pipeline_status {0} time :{1}".format(pipeline.name, elapsed_time))

        except Exception as e:
            log.exception(e)
            pipeline_status.error = traceback.format_exc()
            pipeline_status.status = ERROR
            log.error(pipeline_status)
        finally:
            log.info("insert_pipeline_monitor")

            if pipeline_topic.type == pipeline_constants.SYSTEM:
                log.info("pipeline_status is {0}".format(pipeline_status))
                log.info("unit status is {0}".format(unit_status_list))
            else:
                if unit_status_list:
                    insert_units_monitor(unit_status_list)
                insert_pipeline_monitor(pipeline_status)
