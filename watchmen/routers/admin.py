from fastapi import APIRouter
from pydantic import BaseModel

from watchmen.space.factors.model import Topic
from watchmen.index import select_domain, generate_suggestion_topic_service, generate_suggestion_factor, \
    save_topic_mapping, load_topic_mapping, SpaceOut, load_space_topic_list
from watchmen.space.row_data import ModelSchema
from watchmen.space.row_data.model_schema_set import ModelSchemaSet
from watchmen.pipeline.mapping import TopicMappingRule
from watchmen.space.space import Space
from watchmen.service.master_space_service import save_master_space

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


@router.post("/admin/space", tags=["admin"])
async def create_empty_space(space):
    master_space = Space(space)
    return save_master_space(master_space)


async def import_row_data():
    pass


async def add_topic_to_space():
    pass


async def add_topic_list_to_space():
    pass




@router.post("/admin/suggestion/topic", tags=["admin"], )
async def generate_suggestion_topic(topic_suggestion: TopicSuggestionIn):
    return generate_suggestion_topic_service(topic_suggestion.lake_schema, topic_suggestion.master_schema)


@router.post("/admin/suggestion/factors", tags=["admin"], )
async def generate_suggestion_factor(factor_suggestion: FactorSuggestionIn):
    return generate_suggestion_factor(factor_suggestion.lake_schema, factor_suggestion.topic)


async def create_pipeline():
    pass


async def add_stage_to_pipeline():
    pass


async def save_stage():
    pass


@router.post("/mapping/topic", tags=["admin"], )
async def save_topic_mapping_http(topic_mapping_rule: TopicMappingRule):
    return save_topic_mapping(topic_mapping_rule)


@router.get("/mapping/topic", tags=["admin"], response_model=TopicMappingRule)
async def load_topic_mapping_http(temp_topic_name: str, topic_name: str):
    return load_topic_mapping(temp_topic_name, topic_name)


@router.get("/space", tags=["admin"], response_model=SpaceOut)
async def load_space_topic_list_http(space_name: str):
    return load_space_topic_list(space_name)


@router.post("/space", tags=["admin"])
async def create_space(space):
    master_space = Space(space)
    return save_master_space(master_space)


@router.post("/space/topic", tags=["admin"])
async def create_topic(topic,space_id):
    pass


async def query_topic_list_by_name(topic_name:str):
    pass


async def query_space_list_by_name(space_name:str):
    pass


async def query_report_list_by_name(report_name:str):
    pass