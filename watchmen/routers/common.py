from fastapi import APIRouter

from watchmen.auth.user import User
from watchmen.space.factors.model import Topic
from watchmen.index import auth_login, auth_logout
from watchmen.space.storage.topic_schema_storage import save_topic, get_topic_by_id, get_topic_by_name

router = APIRouter()


@router.get("/health")
async def health():
    return {"health": True}


@router.post("/auth/login")
async def login(user: User):
    return auth_login(user)


@router.post("/auth/logout")
async def logout(user: User):
    return auth_logout(user)


async def save_topic_http(topic:Topic):
    return save_topic(topic)


async def load_topic(topic_id:str):
    return get_topic_by_id(topic_id)


async def save_topic_relationship(topic_relationship):
    pass


async def load_topic_by_name_http(topic_name: str):
    return get_topic_by_name(topic_name)


async def fuzzy_query_topic(topic_name:str):


    pass


async def fuzzy_query_factor(factor_name:str):
    pass