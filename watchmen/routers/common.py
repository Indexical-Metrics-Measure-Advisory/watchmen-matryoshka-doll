import logging

from fastapi import APIRouter

from watchmen.collection.model.topic_event import TopicEvent
from watchmen.common.constants import pipeline_constants
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.pipeline.single.pipeline_service import run_pipeline
from watchmen.pipeline.single.stage.unit.utils.units_func import add_audit_columns, INSERT
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_by_topic_id
from watchmen.topic.storage.topic_data_storage import save_topic_instance, find_topic_data_by_id_and_topic_name
from watchmen.topic.storage.topic_schema_storage import get_topic

router = APIRouter()

log = logging.getLogger("app." + __name__)


@router.get("/health", tags=["common"])
async def health():
    return {"health": True}


@router.post("/topic/data", tags=["common"])
async def save_topic_data(topic_event: TopicEvent):
    # TODO user check URP

    topic = get_topic(topic_event.code)
    if topic is None:
        raise Exception("topic name does not exist")

    add_audit_columns(topic_event.data, INSERT)
    save_topic_instance(topic_event.code, topic_event.data)
    await __trigger_pipeline(topic_event)
    return {"received": True}


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
            log.info("rerun topic {0} and pipeline {1}".format(topic_name,pipeline.pipelineId))
            run_pipeline(pipeline, instance)
    return {"received": True}
