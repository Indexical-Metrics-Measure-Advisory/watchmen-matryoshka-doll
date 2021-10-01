
import asyncio
import logging

from fastapi import APIRouter, Depends

from watchmen.collection.model.topic_event import TopicEvent
from watchmen.common import deps
from watchmen.common.model.topic import Topic
from watchmen.common.model.user import User
from watchmen.pipeline.service.pipeline_service import save_topic_data, get_input_data, run_pipeline
from watchmen.topic.storage.topic_schema_storage import get_topic

router = APIRouter()

log = logging.getLogger("app." + __name__)


@router.get("/health", tags=["pipeline"])
async def health():
    return {"health": True}


def __load_topic_definition(topic_name: str, current_user: User) -> Topic:
    topic = get_topic(topic_name, current_user)
    if topic is None:
        raise Exception(f"{topic_name} topic name does not exist")
    else:
        return topic


@router.post("/pipeline/data/async", tags=["pipeline"])
async def push_pipeline_data_async(topic_event: TopicEvent, current_user: User = Depends(deps.get_current_user)):
    topic = __load_topic_definition(topic_event.code, current_user)
    data = get_input_data(topic, topic_event)
    save_topic_data(topic, data, current_user)
    asyncio.ensure_future(run_pipeline(topic_event, current_user))
    return {"received": True}


@router.post("/pipeline/data", tags=["pipeline"])
async def push_pipeline_data(topic_event: TopicEvent, current_user: User = Depends(deps.get_current_user)):
    topic = __load_topic_definition(topic_event.code, current_user)
    data = get_input_data(topic, topic_event)
    save_topic_data(topic, data, current_user)
    await run_pipeline(topic_event, current_user)
    return {"received": True}

