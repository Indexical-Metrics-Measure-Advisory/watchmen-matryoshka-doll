from bson import json_util
from fastapi import APIRouter, Body
from pydantic import BaseModel

from watchmen.common.pagination import Pagination
from watchmen.index import select_domain, generate_suggestion_topic_service, generate_suggestion_factor, \
    save_topic_mapping, load_topic_mapping, SpaceOut, load_space_topic_list
from watchmen.pipeline.mapping.topic_mapping_rule import TopicMappingRule
from watchmen.raw_data_back.model_schema import ModelSchema

from watchmen.raw_data_back.model_schema_set import ModelSchemaSet
from watchmen.space.service.admin import create_space, update_space_by_id

from watchmen.space.space import Space
from watchmen.space.storage.space_storage import  query_space_with_pagination
from watchmen.topic.service.topic_service import create_topic_schema, update_topic_schema
from watchmen.topic.storage.topic_schema_storage import query_topic_list_with_pagination
from watchmen.topic.topic import Topic
from fastapi import  File

router = APIRouter()


class TopicSuggestionIn(BaseModel):
    lake_schema_set: ModelSchemaSet = None
    master_schema: Space = None


class FactorSuggestionIn(BaseModel):
    lake_schema: ModelSchema = None
    topic: Topic = None


# CORE ADMIN PATH

@router.get("/admin/space/domain", tags=["admin"], response_model=Space)
async def create_space_from_domain_template(name: str):
    return select_domain(name)





@router.post("/upload/files/", tags=["admin"])
async def import_raw_data(file: bytes = File(...)):

    # unzip_file()


    return {"file_size": len(file)}


async def add_topic_to_space():
    pass


async def add_topic_list_to_space():
    pass


@router.post("/admin/suggestion/topic", tags=["admin"])
async def generate_suggestion_topic(topic_suggestion: TopicSuggestionIn):
    return generate_suggestion_topic_service(topic_suggestion.lake_schema, topic_suggestion.master_schema)


@router.post("/admin/suggestion/factors", tags=["admin"])
async def generate_suggestion_factor(factor_suggestion: FactorSuggestionIn):
    return generate_suggestion_factor(factor_suggestion.lake_schema, factor_suggestion.topic)


async def create_pipeline():
    pass


async def add_stage_to_pipeline():
    pass


async def save_stage():
    pass


@router.post("/mapping/topic", tags=["admin"] )
async def save_topic_mapping_http(topic_mapping_rule: TopicMappingRule):
    return save_topic_mapping(topic_mapping_rule)


@router.get("/mapping/topic", tags=["admin"], response_model=TopicMappingRule)
async def load_topic_mapping_http(temp_topic_name: str, topic_name: str):
    return load_topic_mapping(temp_topic_name, topic_name)


@router.get("/space", tags=["admin"], response_model=SpaceOut)
async def load_space_topic_list_http(space_name: str):
    return load_space_topic_list(space_name)


### NEW

@router.post("/space", tags=["admin"])
async def create_empty_space(space:Space):
    return create_space(space)


@router.post("/update/space", tags=["admin"])
async def update_space(space_id:int,space:Space= Body(...)):
    return update_space_by_id(space_id,space)


@router.post("/space/name", tags=["admin"])
async def query_space_list(query_name:str,pagination: Pagination= Body(...)):
    space_list= query_space_with_pagination(query_name,pagination)
    return json_util.dumps(space_list)


@router.post("/topic", tags=["admin"])
async def create_topic(topic:Topic):
    return create_topic_schema(topic)


@router.post("/update/topic", tags=["admin"])
async def update_topic(topic_id,topic:Topic=Body(...)):
    topic = Topic.parse_obj(topic)
    return update_topic_schema(topic_id,topic)


@router.post("/topic/name", tags=["admin"])
async def query_topic_list_by_name(query_name: str, pagination: Pagination= Body(...)):
    result = query_topic_list_with_pagination(query_name,pagination)
    return json_util.dumps(result)




