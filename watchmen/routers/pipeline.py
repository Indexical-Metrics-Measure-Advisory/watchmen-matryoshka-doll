import logging

from fastapi import APIRouter, Depends

from watchmen.common.model.user import User
from watchmen.collection.model.topic_event import TopicEvent
from watchmen.common import deps
from watchmen.raw_data.service.import_raw_data import import_raw_topic_data
from watchmen.topic.storage.topic_schema_storage import get_topic

router = APIRouter()

log = logging.getLogger("app." + __name__)


@router.get("/health", tags=["pipeline"])
async def health():
    return {"health": True}



def __load_topic_definition(topic_name:str,current_user):
    topic = get_topic(topic_name, current_user)
    if topic is None:
        raise Exception(f"{topic_name} topic name does not exist")
    else:
        return topic





@router.post("/topic/data/async", tags=["pipeline"])
async def save_topic_data(topic_event: TopicEvent, current_user: User = Depends(deps.get_current_user)):
    # TODO user check URP
    topic = __load_topic_definition(topic_event.code, current_user)

    await import_raw_topic_data(topic_event, current_user)
    # fire_and_forget(task)
    return {"received": True}


@router.post("/topic/data", tags=["pipeline"])
async def save_topic_data(topic_event: TopicEvent, current_user: User = Depends(deps.get_current_user)):
    # TODO user check URP
    topic = get_topic(topic_event.code, current_user)
    if topic is None:
        raise Exception(topic_event.code + " topic name does not exist")




    await import_raw_topic_data(topic_event, current_user)
    # fire_and_forget(task)
    return {"received": True}