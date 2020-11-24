###
# 1. select basic domain for example insurance product ,marketing
# 2. read json from connector
# 3. generate basic lake base on json data
# 4. match lake with domain  knowledge dataset and provide suggestions
# 5. link knowledge domain to lake
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from watchmen.auth.user import User
from watchmen.factors.model.topic import Topic
from watchmen.index import save_topic_mapping, load_topic_mapping, load_space_topic_list, SpaceOut
from watchmen.lake.model_schema import ModelSchema
from watchmen.lake.model_schema_set import ModelSchemaSet
from watchmen.mapping.topic_mapping_rule import TopicMappingRule
from watchmen.master.master_space import MasterSpace
from .index import select_domain, generate_suggestion_topic_service, auth_login, auth_logout, generate_suggestion_factor

app = FastAPI()


class TopicSuggestionIn(BaseModel):
    lake_schema_set: ModelSchemaSet = None
    master_schema: MasterSpace = None


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



## ADMIN API


@app.get("/select/domain", response_model=MasterSpace)
async def domain(name: str):
    return select_domain(name)


@app.post("/suggestion/topic")
async def generate_suggestion_topic(topic_suggestion: TopicSuggestionIn):
    return generate_suggestion_topic_service(topic_suggestion.lake_schema, topic_suggestion.master_schema)


@app.post("/suggestion/factors")
async def generate_suggestion_topic(factor_suggestion: FactorSuggestionIn):
    return generate_suggestion_factor(factor_suggestion.lake_schema, factor_suggestion.topic)


@app.post("/mapping/topic")
async def save_topic_mapping_http(topic_mapping_rule:TopicMappingRule):
    return save_topic_mapping(topic_mapping_rule)


@app.get("/mapping/topic", response_model=TopicMappingRule)
async def load_topic_mapping_http(temp_topic_name:str,topic_name:str):
    return load_topic_mapping(temp_topic_name,topic_name)


@app.get("/space", response_model=SpaceOut)
async def load_space_topic_list_http(space_name:str):
    return load_space_topic_list(space_name)


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


# TODO management topic service

# TODO collection data service

async def collection_data(template_space_name:str,instance_data:str,pipeline_name:str):
    pass

# TODO monitoring service

async def load_monitoring_data_by_pipeline_trace_id(pipeline_trace_id:str):
    pass

# TODO user cooperation API


async def share_dashboard_url(to:str):
    pass



# @app.get("/generate/{key}/{path}", response_model=ModelSchema)
# async def generate_schema(key: str, path: str):
#     return generate_basic_schema(key, path)



## Console API

async def load_space_list_by_user():
    pass


async def load_space_by_id(id: str):
    pass


async def sort_space_by_sort_type():
    pass





async def load_dashboard_list_by_user():
    pass


async def load_dashboard_by_id(id: str):
    pass

# async def sort_space_by_sort_type():
#     pass


async def connect_to_space():
    pass


async def create_dashboard():
    pass


async def load_subject_by_group():
    pass


async def add_subject_to_group():
    pass


async def load_subject_groups_by_space_id():
    pass


async def load_available_resources_by_space_id():
    pass


async def save_subject_definition():
    pass


async def load_subject_definition():
    pass


async def load_instance_data_by_subject_id():
    pass


async def load_reports_by_subject_id():
    pass

# TODO  user session data
###
# pin and unpin
# position for available resources
# ##





