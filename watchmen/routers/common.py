from fastapi import APIRouter

from watchmen.collection.model.topic_event import TopicEvent
from watchmen.pipeline.index import trigger_pipeline
from watchmen.pipeline.model.trigger_type import TriggerType
from watchmen.topic.storage.topic_data_storage import save_topic_instance
from watchmen.topic.storage.topic_schema_storage import get_topic

router = APIRouter()


@router.get("/health", tags=["common"])
async def health():
    return {"health": True}


@router.post("/topic/data", tags=["common"])
async def save_topic_data(topic_event: TopicEvent):
    # TODO user check URP

    # print(topic_event.code)

    topic = get_topic(topic_event.code)

    # print(topic)
    if topic is None:
        raise Exception("topic name does not exist")

    save_topic_instance(topic_event.code, topic_event.data)
    trigger_pipeline(topic_event.code, topic_event.data, TriggerType.insert)
