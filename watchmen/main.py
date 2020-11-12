###
# 1. select basic domain for example insurance product ,marketing
# 2. read json from connector
# 3. generate basic lake base on json data
# 4. match lake with domain  knowledge dataset and provide suggestions
# 5. link knowledge domain to lake

from fastapi import FastAPI
from pydantic import BaseModel

from watchmen.auth.user import User
from watchmen.factors.model.topic import Topic
from watchmen.lake.model_schema import ModelSchema
from watchmen.lake.model_schema_set import ModelSchemaSet
from watchmen.master.master_schema import MasterSchema
from .index import select_domain, generate_suggestion_topic_service, auth_login, auth_logout, generate_suggestion_factor

app = FastAPI()


class TopicSuggestionIn(BaseModel):
    lake_schema_set: ModelSchemaSet = None
    master_schema: MasterSchema = None


class FactorSuggestionIn(BaseModel):
    lake_schema: ModelSchema = None
    topic: Topic = None


@app.get("/health")
async def health():
    return {"health": True}


@app.post("/auth/login")
async def login(user: User):
    return auth_login(user)


@app.post("/auth/logout")
async def logout(user: User):
    return auth_logout(user)


@app.get("/select/domain", response_model=MasterSchema)
async def domain(name: str):
    return select_domain(name)


@app.post("/suggestion/topic")
async def generate_suggestion_topic(topic_suggestion: TopicSuggestionIn):
    return generate_suggestion_topic_service(topic_suggestion.lake_schema, topic_suggestion.master_schema)


@app.post("/suggestion/factors")
async def generate_suggestion_topic(factor_suggestion: FactorSuggestionIn):
    return generate_suggestion_factor(factor_suggestion.lake_schema, factor_suggestion.topic)

# @app.get("/generate/{key}/{path}", response_model=ModelSchema)
# async def generate_schema(key: str, path: str):
#     return generate_basic_schema(key, path)
