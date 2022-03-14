import asyncio
import logging

from fastapi import APIRouter, Depends
from model.model.common.user import User
from model.model.topic.topic import Topic

from watchmen.collection.model.topic_event import TopicEvent
from watchmen.common import deps
from watchmen_boot.guid.snowflake import get_surrogate_key
from watchmen.pipeline.service.pipeline_service import save_topic_data, get_input_data, run_pipeline
from watchmen.topic.storage.topic_schema_storage import get_topic, get_topic_by_name_and_tenant_id

router = APIRouter()

log = logging.getLogger("app." + __name__)


@router.get("/health", tags=["pipeline"])
async def health():
    return {"health": True}


async def __load_topic_definition(topic_name: str, current_user: User) -> Topic:
    topic = get_topic(topic_name, current_user)
    if topic is None:
        raise Exception(f"{topic_name} topic name does not exist")
    else:
        return topic


@router.post("/pipeline/data/async", tags=["pipeline"])
async def push_pipeline_data_async(topic_event: TopicEvent, current_user: User = Depends(deps.get_current_user)):
    trace_id = get_surrogate_key()
    #
    # create_raw_topic_instance
    topic = await __load_topic_definition(topic_event.code, current_user)
    data = get_input_data(topic, topic_event)
    await save_topic_data(topic, data, current_user)
    asyncio.ensure_future(run_pipeline(topic_event, current_user, trace_id))
    return {"received": True, "trace_id": trace_id}


@router.post("/pipeline/data", tags=["pipeline"])
async def push_pipeline_data(topic_event: TopicEvent, current_user: User = Depends(deps.get_current_user)):
    trace_id = get_surrogate_key()
    topic = await __load_topic_definition(topic_event.code, current_user)
    data = get_input_data(topic, topic_event)
    await save_topic_data(topic, data, current_user)
    await run_pipeline(topic_event, current_user, trace_id)
    return {"received": True, "trace_id": trace_id}


@router.post("/pipeline/data/async/tenant", tags=["pipeline"])
async def push_pipeline_data_async_tenant(topic_event: TopicEvent, current_user: User = Depends(deps.get_current_user)):
    trace_id = get_surrogate_key()
    topic = get_topic_by_name_and_tenant_id(topic_event.code,
                                            topic_event.tenantId)
    data = get_input_data(topic, topic_event)
    current_user.tenantId = topic_event.tenantId
    await save_topic_data(topic, data, current_user)
    asyncio.ensure_future(run_pipeline(topic_event, current_user, trace_id))
    return {"received": True, "trace_id": trace_id}
