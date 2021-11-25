import asyncio
import logging
import time
import traceback
from datetime import datetime
from functools import lru_cache

from model.model.pipeline.trigger_type import TriggerType

import watchmen
from watchmen.common.constants import pipeline_constants
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import get_id_name_by_datasource
from watchmen.config.config import settings
from watchmen.database.datasource.container import data_source_container
from watchmen.monitor.model.pipeline_monitor import PipelineRunStatus, StageRunStatus
from watchmen.monitor.services import pipeline_monitor_service
from watchmen.pipeline.core.context.pipeline_context import PipelineContext
from watchmen.pipeline.core.context.stage_context import StageContext
from watchmen.pipeline.core.parameter.parse_parameter import parse_parameter_joint
from watchmen.pipeline.core.worker.stage_worker import run_stage
from watchmen.pipeline.utils.constants import PIPELINE_UID, FINISHED, ERROR
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id, get_topic_by_name

log = logging.getLogger("app." + __name__)


@lru_cache(maxsize=20)
def __build_merge_key(topic_name, trigger_type):
    return topic_name + "_" + trigger_type.value


def __merge_pipeline_data(pipeline_trigger_merge_list):
    merge_context = {}
    # id_dict = {}
    for pipeline_data in pipeline_trigger_merge_list:

        if pipeline_data.topicName in merge_context:
            data_list = merge_context[pipeline_data.topicName].get(pipeline_data.triggerType.value, [])
            data_list.append(pipeline_data.data)
            merge_context[pipeline_data.topicName][pipeline_data.triggerType.value] = data_list
        else:
            merge_context[pipeline_data.topicName] = {pipeline_data.triggerType.value: [pipeline_data.data]}

    return merge_context


def __build_merge_key(topic_name, trigger_type):
    return topic_name + "_" + trigger_type.value


def __trigger_all_pipeline(pipeline_trigger_merge_list, current_user=None, trace_id=None):
    after_merge_list = __merge_pipeline_data(pipeline_trigger_merge_list)

    for topic_name, item in after_merge_list.items():
        merge_data = {}
        topic = get_topic_by_name(topic_name)
        if TriggerType.update.value in item:
            for update_data in item[TriggerType.update.value]:
                old_value = update_data[pipeline_constants.OLD]
                pk = old_value[
                    get_id_name_by_datasource(data_source_container.get_data_source_by_id(topic.dataSourceId))]
                if pk in merge_data:
                    merge_data[pk][pipeline_constants.NEW].update(update_data[pipeline_constants.NEW])
                else:
                    merge_data[pk] = {pipeline_constants.NEW: update_data[pipeline_constants.NEW],
                                      pipeline_constants.OLD: update_data[pipeline_constants.OLD]}

                for key, data in merge_data.items():
                    watchmen.pipeline.index.trigger_pipeline(topic_name, data, TriggerType.update, current_user,
                                                             trace_id)
        if TriggerType.insert.value in item:
            for insert_data in item[TriggerType.insert.value]:
                watchmen.pipeline.index.trigger_pipeline(topic_name, insert_data, TriggerType.insert, current_user,
                                                         trace_id)


def should_run(pipeline_context: PipelineContext) -> bool:
    pipeline = pipeline_context.pipeline
    if pipeline.on is None:
        return True
    current_data = pipeline_context.currentOfTriggerData
    variables = pipeline_context.variables
    return parse_parameter_joint(pipeline.on, current_data, variables)


async def sync_pipeline_monitor_log(pipeline_status):
    pipeline_monitor_service.sync_pipeline_monitor_data(pipeline_status)


def run_pipeline(pipeline_context: PipelineContext):
    pipeline = pipeline_context.pipeline
    data = pipeline_context.data
    pipeline_status = PipelineRunStatus(pipelineId=pipeline.pipelineId, uid=get_surrogate_key(),
                                        startTime=datetime.now().replace(tzinfo=None), topicId=pipeline.topicId,
                                        tenantId=pipeline_context.currentUser.tenantId,
                                        traceId=pipeline_context.traceId, pipelineName=pipeline.name)
    pipeline_status.oldValue = data[pipeline_constants.OLD]
    pipeline_status.newValue = data[pipeline_constants.NEW]
    pipeline_status.currentUser = pipeline_context.currentUser
    if pipeline_context.currentUser is None:
        raise Exception("pipeline_context currentUser is None")

    if pipeline.enabled:
        pipeline_topic = get_topic_by_id(pipeline.topicId)
        pipeline_status.pipelineTopicName = pipeline_topic.name
        pipeline_context = PipelineContext(pipeline, data, pipeline_context.currentUser, pipeline_context.traceId)
        pipeline_context.variables[PIPELINE_UID] = pipeline_status.uid
        pipeline_context.pipelineTopic = pipeline_topic
        pipeline_context.pipelineStatus = pipeline_status
        start = time.time()
        if should_run(pipeline_context):
            try:
                for stage in pipeline.stages:
                    stage_run_status = StageRunStatus(name=stage.name)
                    stage_context = StageContext(pipeline_context, stage, stage_run_status)
                    stage_run_status.name = stage.name
                    run_stage(stage_context, stage_run_status)
                    pipeline_status.stages.append(stage_context.stageStatus)

                elapsed_time = time.time() - start
                pipeline_status.completeTime = elapsed_time
                pipeline_status.status = FINISHED
                log.info("run pipeline \"{0}\" spend time \"{1}\" ".format(pipeline.name, elapsed_time))
                if pipeline_topic.kind is None or pipeline_topic.kind != pipeline_constants.SYSTEM:
                    __trigger_all_pipeline(pipeline_context.pipeline_trigger_merge_list, pipeline_context.currentUser,
                                           pipeline_context.traceId)
            except Exception as e:
                trace = traceback.format_exc()
                log.error(trace)
                pipeline_status.error = trace
                pipeline_status.status = ERROR
            finally:
                if settings.PIPELINE_MONITOR_ON:
                    if pipeline_topic.kind is not None and pipeline_topic.kind == pipeline_constants.SYSTEM:
                        log.debug("pipeline_status is {0}".format(pipeline_status))
                    else:
                        asyncio.ensure_future(sync_pipeline_monitor_log(pipeline_status))
                else:
                    log.info("pipeline {0} status is {1}".format(pipeline.name, pipeline_status.status))
