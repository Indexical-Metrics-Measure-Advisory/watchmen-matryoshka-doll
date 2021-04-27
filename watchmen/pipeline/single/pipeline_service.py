import importlib
import logging
import time
import traceback
from datetime import datetime
from functools import lru_cache

import watchmen.monitor.services.pipeline_monitor_service
from watchmen.common.constants import pipeline_constants
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.config.config import settings
from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus, UnitRunStatus, StageRunStatus
# from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
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


def __get_unique_key_name() -> str:
    if settings.STORAGE_ENGINE == "mongo":
        return "_id"
    else:
        return "id_"


def __build_merge_key(topic_name, trigger_type):
    return topic_name + "_" + trigger_type.value


def __merge_pipeline_data(pipeline_trigger_merge_list):
    merge_context = {}
    id_dict = {}
    for pipeline_data in pipeline_trigger_merge_list:
        # print("-----pipeline", pipeline_data)
        key = __build_merge_key(pipeline_data.topicName, pipeline_data.triggerType)
        if pipeline_data.topicName in merge_context:
            data_list = merge_context[pipeline_data.topicName].get(pipeline_data.triggerType.value, [])
            data_list.append(pipeline_data.data)
            merge_context[pipeline_data.topicName][pipeline_data.triggerType.value] = data_list
        else:
            merge_context[pipeline_data.topicName] = {pipeline_data.triggerType.value: [pipeline_data.data]}
    # print(merge_context)
    return merge_context


def __trigger_all_pipeline(pipeline_trigger_merge_list):
    # print(pipeline_trigger_merge_list)
    after_merge_list = __merge_pipeline_data(pipeline_trigger_merge_list)
    # print(after_merge_list)
    for topic_name, item in after_merge_list.items():
        log.info("merge_topic:{0}".format(topic_name))
        merge_data = {}
        if TriggerType.update.value in item:
            for update_data in item[TriggerType.update.value]:
                # print("------------------------")
                # print("update_data", update_data)
                # print("------------------------")
                old_value = update_data[pipeline_constants.OLD]
                pk = old_value[__get_unique_key_name()]
                if pk in merge_data:
                    merge_data[pk][pipeline_constants.NEW].update(update_data[pipeline_constants.NEW])
                else:
                    merge_data[pk] = {pipeline_constants.NEW: update_data[pipeline_constants.NEW],
                                      pipeline_constants.OLD: update_data[pipeline_constants.OLD]}

                for key, data in merge_data.items():
                    watchmen.pipeline.index.trigger_pipeline(topic_name, data, TriggerType.update)
        if TriggerType.insert.value in item:
            for insert_data in item[TriggerType.insert.value]:
                watchmen.pipeline.index.trigger_pipeline(topic_name, insert_data, TriggerType.insert)


def run_pipeline(pipeline: Pipeline, data):
    pipeline_status = PipelineRunStatus(pipelineId=pipeline.pipelineId, uid=get_surrogate_key(),
                                        startTime=datetime.now(), topicId=pipeline.pipelineId)
    pipeline_status.oldValue = data[pipeline_constants.OLD]
    pipeline_status.newValue = data[pipeline_constants.NEW]

    # trigger_context =

    # pipeline = Pipeline.parse_obj(pipeline)
    if pipeline.enabled:
        pipeline_topic = get_topic_by_id(pipeline.topicId)
        log.info("start run pipeline {0}".format(pipeline.name))
        context = {PIPELINE_UID: pipeline_status.uid}
        if __check_condition(pipeline, pipeline_topic, data, context):
            try:
                start = time.time()

                pipeline_trigger_merge_list = []
                for stage in pipeline.stages:

                    if __check_condition(stage, pipeline_topic, data, context):
                        stage_run_status = StageRunStatus()
                        stage_run_status.name = stage.name
                        log.info("stage name {0}".format(stage.name))

                        for unit in stage.units:

                            if unit.do is not None:
                                match_result = __check_condition(unit, pipeline_topic, data, context)
                                # print("match_result",match_result)
                                if match_result:
                                    unit_run_status = UnitRunStatus()
                                    for action in unit.do:
                                        start = time.time()
                                        func = find_action_type_func(convert_action_type(action.type), action,
                                                                     pipeline_topic)
                                        # call dynamic action in action folder
                                        # TODO [future] custom folder
                                        out_result, unit_action_status, trigger_pipeline_data_list = func(data, context)
                                        elapsed_time = time.time() - start

                                        print("elapsed_time ：" + action.type, elapsed_time)

                                        if trigger_pipeline_data_list:
                                            pipeline_trigger_merge_list = [*pipeline_trigger_merge_list,
                                                                           *trigger_pipeline_data_list]

                                        log.info("out_result :{0}".format(out_result))
                                        context = {**context, **out_result}
                                        # print("context : ",context)
                                        unit_run_status.actions.append(unit_action_status)
                                    stage_run_status.units.append(unit_run_status)
                            else:
                                log.debug("action stage unit  {0} do is None".format(stage.name))
                        pipeline_status.stages.append(stage_run_status)
                elapsed_time = time.time() - start
                pipeline_status.completeTime = elapsed_time
                pipeline_status.status = FINISHED
                log.debug("pipeline_status {0} time :{1}".format(pipeline.name, elapsed_time))
                # # print(pipeline_topic.kind)
                # print("------------------------")
                # print(len(pipeline_trigger_merge_list))
                # print("-----------------------")
                if pipeline_topic.kind is None or pipeline_topic.kind != pipeline_constants.SYSTEM:
                    __trigger_all_pipeline(pipeline_trigger_merge_list)
                ## trigger_pipeline()

            except Exception as e:
                log.exception(e)
                pipeline_status.error = traceback.format_exc()
                pipeline_status.status = ERROR
                log.error(pipeline_status)
            finally:
                if pipeline_topic.kind is not None and pipeline_topic.kind == pipeline_constants.SYSTEM:
                    # log.debug("pipeline_status is {0}".format(pipeline_status))
                    pass
                else:
                    pass
                    # print("sync pipeline monitor")
                    # watchmen.monitor.services.pipeline_monitor_service.sync_pipeline_monitor_data(pipeline_status)
