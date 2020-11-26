from fastapi import APIRouter

from watchmen.auth.user import User
from watchmen.factors.model.topic import Topic
from watchmen.index import auth_login, auth_logout

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


async def save_topic(topic:Topic):
    pass


async def load_topic(topic_id:str):
    pass


async def save_topic_relationship(topic_relationship):
    pass


async def fuzzy_query_topic(topic_name:str):
    pass


async def fuzzy_query_factor(factor_name:str):
    pass