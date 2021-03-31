import importlib
import logging
import time
import traceback
from datetime import datetime
from functools import lru_cache

import watchmen.monitor.services.pipeline_monitor_service
from watchmen.common.constants import pipeline_constants
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus, UnitRunStatus, StageRunStatus
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.pipeline.single.stage.unit.mongo.index import __check_condition
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


def run_pipeline(pipeline: Pipeline, data):
    pipeline_status = PipelineRunStatus(pipelineId=pipeline.pipelineId, uid=get_surrogate_key(),
                                        startTime=datetime.now(), topicId=pipeline.pipelineId)
    pipeline_status.oldValue = data[pipeline_constants.OLD]
    pipeline_status.newValue = data[pipeline_constants.NEW]

    if pipeline.enabled:
        pipeline_topic = get_topic_by_id(pipeline.topicId)
        log.info("start run pipeline {0}".format(pipeline.name))
        context = {PIPELINE_UID: pipeline_status.uid}
        if __check_condition(pipeline, pipeline_topic, data):
            try:
                start = time.time()
                for stage in pipeline.stages:
                    if __check_condition(stage, pipeline_topic, data):
                        stage_run_status = StageRunStatus()
                        stage_run_status.name = stage.name
                        log.info("stage name {0}".format(stage.name))
                        for unit in stage.units:
                            if unit.do is not None and __check_condition(unit, pipeline_topic, data):
                                unit_run_status = UnitRunStatus()
                                for action in unit.do:
                                    func = find_action_type_func(convert_action_type(action.type), action,
                                                                 pipeline_topic)
                                    # call dynamic action in action folder
                                    # TODO [future] custom folder
                                    out_result, unit_action_status = func(data, context)
                                    log.debug("out_result :{0}".format(out_result))
                                    context = {**context, **out_result}
                                    unit_run_status.actions.append(unit_action_status)
                                stage_run_status.units.append(unit_run_status)
                            else:
                                log.info("action stage unit  {0} do is None".format(stage.name))
                        pipeline_status.stages.append(stage_run_status)
                elapsed_time = time.time() - start
                pipeline_status.completeTime = elapsed_time
                pipeline_status.status = FINISHED
                log.info("pipeline_status {0} time :{1}".format(pipeline.name, elapsed_time))

            except Exception as e:
                log.exception(e)
                pipeline_status.error = traceback.format_exc()
                pipeline_status.status = ERROR
                log.error(pipeline_status)
            finally:
                if pipeline_topic.kind is not None and pipeline_topic.kind == pipeline_constants.SYSTEM:
                    log.debug("pipeline_status is {0}".format(pipeline_status))
                else:
                    print("sync pipeline monitor")
                    watchmen.monitor.services.pipeline_monitor_service.sync_pipeline_monitor_data(pipeline_status)
