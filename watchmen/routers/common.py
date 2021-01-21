from fastapi import APIRouter

from watchmen.collection.model.topic_event import TopicEvent
from watchmen.topic.storage.topic_data_storage import save_topic_instance

router = APIRouter()


@router.get("/health", tags=["common"])
async def health():
    return {"health": True}


@router.post("/topic/data", tags=["common"])
async def save_topic_data(topic_event: TopicEvent):
    save_topic_instance(topic_event.code, topic_event.data)
