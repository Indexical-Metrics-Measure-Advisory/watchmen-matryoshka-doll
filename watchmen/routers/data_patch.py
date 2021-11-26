import logging
from typing import List

from fastapi import APIRouter, Depends, Body
from model.model.common.user import User
from model.model.pipeline.pipeline import Pipeline

from watchmen.common import deps
from watchmen.pipeline.core.context.pipeline_context import PipelineContext
from watchmen.pipeline.core.worker.pipeline_worker import run_pipeline
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_by_topic_id
from watchmen.topic.storage.topic_data_storage import find_topic_data_by_id_and_topic_name, \
    update_topic_instance, save_topic_instance
from watchmen.topic.storage.topic_schema_storage import get_topic_by_name, get_topic

router = APIRouter()

log = logging.getLogger("app." + __name__)


@router.get("/health", tags=["patch"])
async def health():
    return {"health": True}


def find_execute_pipeline_list(pipeline_id, pipeline_list) -> List[Pipeline]:
    if pipeline_id is None:
        return pipeline_list
    else:
        for pipeline in pipeline_list:
            if pipeline.pipelineId == pipeline_id:
                return [pipeline]


@router.post("/data/rerun", tags=["patch"])
async def rerun_pipeline(topic_name, instance_id, pipeline_id=None,
                         current_user: User = Depends(deps.get_current_user)):
    topic = get_topic(topic_name)
    instance = find_topic_data_by_id_and_topic_name(topic, instance_id)
    pipeline_list = load_pipeline_by_topic_id(topic.topicId)
    for pipeline in find_execute_pipeline_list(pipeline_id, pipeline_list):
        log.info("rerun topic {0} and pipeline {1}".format(topic_name, pipeline.pipelineId))
        pipeline_context = PipelineContext(pipeline, instance, current_user)
        run_pipeline(pipeline_context)
    return {"received": True}


@router.post("/data/patch", tags=["patch"])
async def patch_topic_instance(topic_name, instance_id=None, instance=Body(...),
                               current_user: User = Depends(deps.get_current_user)):
    topic = get_topic_by_name(topic_name)
    if instance_id is None:
        save_topic_instance(topic, instance, current_user)
    else:
        result = find_topic_data_by_id_and_topic_name(topic, instance_id)
        if result is not None:
            update_topic_instance(topic, instance, instance_id)
        else:
            raise Exception("instance ID {0} could not find any data for update".format(instance_id))
