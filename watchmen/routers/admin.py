from typing import List

from fastapi import APIRouter, Body
from pydantic import BaseModel

from watchmen.auth.storage.user import create_user_storage, query_users_by_name_with_pagination, get_user_list_by_ids, \
    get_user, load_user_list_by_name
from watchmen.auth.storage.user_group import create_user_group_storage, query_user_groups_by_name_with_paginate, \
    get_user_group_list_by_ids, get_user_group, load_group_list_by_name
from watchmen.auth.user import User
from watchmen.auth.user_group import UserGroup
from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.index import generate_suggestion_topic_service, generate_suggestion_factor
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.pipeline.model.pipeline_flow import PipelineFlow
from watchmen.pipeline.storage.pipeline_storage import update_pipeline, create_pipeline, load_pipeline_by_topic_id
from watchmen.raw_data.model_schema import ModelSchema
from watchmen.raw_data.model_schema_set import ModelSchemaSet
from watchmen.space.service.admin import create_space, update_space_by_id
from watchmen.space.space import Space
from watchmen.space.storage.space_storage import query_space_with_pagination, get_space_by_id, get_space_list_by_ids
from watchmen.topic.service.topic_service import create_topic_schema, update_topic_schema
from watchmen.topic.storage.topic_schema_storage import query_topic_list_with_pagination, get_topic_by_id, \
    get_topic_list_by_ids, load_all_topic_list, load_topic_list_by_name
from watchmen.topic.topic import Topic

router = APIRouter()


class TopicSuggestionIn(BaseModel):
    lake_schema_set: ModelSchemaSet = None
    master_schema: Space = None


class FactorSuggestionIn(BaseModel):
    lake_schema: ModelSchema = None
    topic: Topic = None


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


# ADMIN

## Space
@router.post("/space", tags=["admin"], response_model=Space)
async def create_space(space: Space):
    return create_space(space)


@router.post("/save/space",tags=["admin"],response_model=Space)
async def save_space(space: Space):
    if space.spaceId is  None:
        return create_space(space)
    else:
        return update_space_by_id(space.spaceId, space)


@router.post("/update/space", tags=["admin"], response_model=Space)
async def update_space(space_id, space: Space = Body(...)):
    return update_space_by_id(space_id, space)


@router.get("/space", tags=["admin"], response_model=Space)
async def load_space(space_id):
    return get_space_by_id(space_id)


@router.post("/space/name", tags=["admin"], response_model=DataPage)
async def query_space_list(query_name: str, pagination: Pagination = Body(...)):
    result = query_space_with_pagination(query_name, pagination)
    return result


@router.post("/space/ids", tags=["admin"], response_model=List[Space])
async def query_space_list_by_ids(space_ids: List[str]):
    return get_space_list_by_ids(space_ids)


## Topic
@router.get("/topic", tags=["admin"], response_model=Topic)
async def load_topic(topic_id):
    # print(topic_id)
    return get_topic_by_id(topic_id)


@router.post("/topic", tags=["admin"], response_model=Topic)
async def create_topic(topic: Topic):
    return create_topic_schema(topic)


@router.post("/save/topic", tags=["admin"], response_model=Topic)
async def save_topic(topic: Topic):
    if topic.topicId is None:
        return create_topic_schema(topic)
    else:
        topic = Topic.parse_obj(topic)
        return update_topic_schema(topic.topicId, topic)


@router.post("/update/topic", tags=["admin"], response_model=Topic)
async def update_topic(topic_id, topic: Topic = Body(...)):
    topic = Topic.parse_obj(topic)
    return update_topic_schema(topic_id, topic)


@router.post("/topic/name", tags=["admin"], response_model=DataPage)
async def query_topic_list_by_name(query_name: str, pagination: Pagination = Body(...)):
    result = query_topic_list_with_pagination(query_name, pagination)
    return result


@router.post("/topic/all", tags=["admin"], response_model=DataPage)
async def query_topic_list_for_pipeline(pagination: Pagination):
    result = load_all_topic_list(pagination)
    return result


@router.get("/query/topic/space", tags=["admin"], response_model=List[Topic])
async def query_topic_list_for_space(query_name: str):
    return load_topic_list_by_name(query_name)


@router.post("/topic/ids", tags=["admin"], response_model=List[Topic])
async def query_topic_list_by_ids(topic_ids: List[str]):
    return get_topic_list_by_ids(topic_ids)


## User
@router.post("/user", tags=["admin"], response_model=User)
async def create_user(user: User):
    return create_user_storage(user)


async def save_user(user: User):
    if user.userId is None:
        pass
    else:
        pass



@router.post("/user/name", tags=["admin"], response_model=DataPage)
async def query_user_list_by_name(query_name: str, pagination: Pagination = Body(...)):
    return query_users_by_name_with_pagination(query_name, pagination)


@router.post("/user/ids", tags=["admin"], response_model=List[User])
async def query_user_list_by_ids(user_ids: List[str]):
    return get_user_list_by_ids(user_ids)


@router.get("/user", tags=["admin"], response_model=User)
async def load_user(user_id: str):
    return get_user(user_id)


@router.get("/query/user/group", tags=["admin"], response_model=List[User])
async def query_user_list_for_user_group(query_name):
    return load_user_list_by_name(query_name)


## User Group
@router.post("/user_group", tags=["admin"], response_model=UserGroup)
async def create_user_group(user_group: UserGroup):
    return create_user_group_storage(user_group)


@router.post("/save/user_group",tags=["admin"],response_model=UserGroup)
async def save_user_group(user_group: UserGroup):
    if user_group.userGroupId is None:
        pass
    else:
        pass



@router.get("/query/user_group/space", tags=["admin"], response_model=List[UserGroup])
async def query_group_list_for_space(query_name: str):
    return load_group_list_by_name(query_name)


@router.get("/user_group", tags=["admin"], response_model=UserGroup)
async def load_user_group(user_group_id):
    return get_user_group(user_group_id)


@router.post("/user_groups/ids", tags=["admin"], response_model=List[UserGroup])
async def query_user_groups_by_ids(user_group_ids: List[str]):
    return get_user_group_list_by_ids(user_group_ids)


@router.post("/user_group/name", tags=["admin"], response_model=DataPage)
async def query_user_groups_list_by_name(query_name: str, pagination: Pagination = Body(...)):
    return query_user_groups_by_name_with_paginate(query_name, pagination)


## pipeline

@router.post("/pipeline", tags=["admin"], response_model=Pipeline)
async def save_pipeline(pipeline: Pipeline):
    result = load_pipeline_by_topic_id(pipeline.topicId)

    if len(result) > 0:
        return update_pipeline(pipeline)
    else:
        return create_pipeline(pipeline)


@router.get("/pipeline", tags=["admin"], response_model=PipelineFlow)
async def load_pipeline(topic_id):
    result = load_pipeline_by_topic_id(topic_id)
    return {"topicId": topic_id,"consume":result,"produce":result}


