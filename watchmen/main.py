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
from .routers import admin, console, common

app = FastAPI()


app.include_router(admin.router)
app.include_router(console.router)
app.include_router(common.router)


#
# class TopicSuggestionIn(BaseModel):
#     lake_schema_set: ModelSchemaSet = None
#     master_schema: MasterSpace = None
#
#
# class FactorSuggestionIn(BaseModel):
#     lake_schema: ModelSchema = None
#     topic: Topic = None


# common api
#






# TODO monitoring service

async def load_monitoring_data_by_pipeline_trace_id(pipeline_trace_id:str):
    pass

# TODO user cooperation API









## inbox

## notifications

## Timeline

## settings

# TODO  user session data
###
# pin and unpin
# position for available resources
# ##





## integration api

async def collection_data(template_space_name:str,instance_data:str,pipeline_name:str):
    pass

