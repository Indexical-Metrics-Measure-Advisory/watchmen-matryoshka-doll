import logging
from typing import List, Any

from fastapi import APIRouter, Depends

from watchmen.auth.user import User
from watchmen.collection.model.topic_event import TopicEvent
from watchmen.common import deps
from watchmen.common.constants import pipeline_constants
from watchmen.common.mongo.index import delete_topic_collection
from watchmen.common.mongo_model import MongoModel
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.single.pipeline_service import run_pipeline
from watchmen.pipeline.single.stage.unit.utils.units_func import add_audit_columns, INSERT
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_by_topic_id
from watchmen.raw_data.service.import_raw_data import import_raw_topic_data
from watchmen.topic.storage.topic_data_storage import save_topic_instance, find_topic_data_by_id_and_topic_name, \
    update_topic_instance, get_topic_instances_all
from watchmen.topic.storage.topic_schema_storage import get_topic

router = APIRouter()

log = logging.getLogger("app." + __name__)


class TopicInstance(MongoModel):
    data: Any = None


@router.get("/health", tags=["common"])
async def health():
    return {"health": True}


@router.post("/topic/data", tags=["common"])
async def save_topic_data(topic_event: TopicEvent):
    # TODO user check URP

    await import_raw_topic_data(topic_event)
    return {"received": True}


@router.get("/topic/data/all", tags=["common"], response_model=List[TopicInstance])
async def load_topic_instance(topic_name, current_user: User = Depends(deps.get_current_user)):
    results = get_topic_instances_all(topic_name)
    instances = []
    for result in results:
        instances.append(TopicInstance(data=result))
    return instances


async def __trigger_pipeline(topic_event):
    trigger_pipeline(topic_event.code, {pipeline_constants.NEW: topic_event.data, pipeline_constants.OLD: None},
                     TriggerType.insert)


@router.post("/topic/data/rerun", tags=["common"])
async def rerun_pipeline(topic_name, instance_id, pipeline_id):
    instance = find_topic_data_by_id_and_topic_name(topic_name, instance_id)
    topic = get_topic(topic_name)
    pipeline_list = load_pipeline_by_topic_id(topic.topicId)
    for pipeline in pipeline_list:
        if pipeline.pipelineId == pipeline_id:
            log.info("rerun topic {0} and pipeline {1}".format(topic_name, pipeline.pipelineId))
            run_pipeline(pipeline, instance)
    return {"received": True}


@router.post("/topic/data/patch", tags=["common"])
async def patch_topic_instance(topic_name, instance, instance_id):
    result = find_topic_data_by_id_and_topic_name(topic_name, instance_id)
    if result is None:
        raise Exception("topic {0} id {1} not found data ".format(topic_name, instance_id))
    else:
        # TODO audit data
        update_topic_instance(topic_name, instance, instance_id)


@router.post("/topic/data/remove", tags=["common"])
async def remove_topic_collection(collections: List[str], current_user: User = Depends(deps.get_current_user)):
    for collection in collections:
        delete_topic_collection(collection)
