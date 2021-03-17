import logging
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException

from watchmen.auth.storage.user import create_user_storage, query_users_by_name_with_pagination, get_user_list_by_ids, \
    get_user, load_user_list_by_name, update_user_storage
from watchmen.auth.storage.user_group import create_user_group_storage, query_user_groups_by_name_with_paginate, \
    get_user_group_list_by_ids, get_user_group, load_group_list_by_name, update_user_group_storage
from watchmen.auth.user import User
from watchmen.auth.user_group import UserGroup
from watchmen.common import deps
from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.common.presto.presto_utils import create_or_update_presto_schema_fields
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.enum.model.enum import Enum
from watchmen.enum.storage.enum_storage import save_enum_to_storage, query_enum_list_with_pagination, load_enum_by_id
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.pipeline.model.pipeline_flow import PipelineFlow
from watchmen.pipeline.model.pipeline_graph import PipelinesGraphics
from watchmen.pipeline.storage.pipeline_storage import update_pipeline, create_pipeline, load_pipeline_by_topic_id, \
    load_pipeline_list, load_pipeline_graph, create_pipeline_graph, update_pipeline_graph, update_pipeline_status, \
    update_pipeline_name, load_pipeline_by_id
from watchmen.report.storage.report_storage import query_report_list_with_pagination
from watchmen.space.service.admin import create_space, update_space_by_id
from watchmen.space.space import Space
from watchmen.space.storage.space_storage import query_space_with_pagination, get_space_by_id, get_space_list_by_ids, \
    load_space_list_by_name
from watchmen.topic.service.topic_service import create_topic_schema, update_topic_schema
from watchmen.topic.storage.topic_schema_storage import query_topic_list_with_pagination, get_topic_by_id, \
    get_topic_list_by_ids, load_all_topic_list, load_topic_list_by_name, load_all_topic
from watchmen.topic.topic import Topic

router = APIRouter()

log = logging.getLogger("app." + __name__)


#
# class TopicSuggestionIn(BaseModel):
#     lake_schema_set: ModelSchemaSet = None
#     master_schema: Space = None
#
#
# class FactorSuggestionIn(BaseModel):
#     lake_schema: ModelSchema = None
#     topic: Topic = None


# @router.post("/admin/suggestion/topic", tags=["admin"])
# async def generate_suggestion_topic(topic_suggestion: TopicSuggestionIn):
#     return generate_suggestion_topic_service(topic_suggestion.lake_schema, topic_suggestion.master_schema)
#
#
# @router.post("/admin/suggestion/factors", tags=["admin"])
# async def generate_suggestion_factor(factor_suggestion: FactorSuggestionIn):
#     return generate_suggestion_factor(factor_suggestion.lake_schema, factor_suggestion.topic)


# ADMIN


@router.post("/space", tags=["admin"], response_model=Space)
async def save_space(space: Space, current_user: User = Depends(deps.get_current_user)):
    if space.spaceId is None or check_fake_id(space.spaceId):
        return create_space(space)
    else:
        return update_space_by_id(space.spaceId, space)


@router.post("/update/space", tags=["admin"], response_model=Space)
async def update_space(space_id, space: Space = Body(...), current_user: User = Depends(deps.get_current_user)):
    return update_space_by_id(space_id, space)


@router.get("/space", tags=["admin"], response_model=Space)
async def load_space(space_id: str, current_user: User = Depends(deps.get_current_user)):
    return get_space_by_id(space_id)


@router.post("/space/name", tags=["admin"], response_model=DataPage)
async def query_space_list(query_name: str, pagination: Pagination = Body(...),
                           current_user: User = Depends(deps.get_current_user)):
    result = query_space_with_pagination(query_name, pagination)
    return result


@router.post("/space/ids", tags=["admin"], response_model=List[Space])
async def query_space_list_by_ids(space_ids: List[str], current_user: User = Depends(deps.get_current_user)):
    return get_space_list_by_ids(space_ids)


@router.get("/query/space/group", tags=["admin"], response_model=List[Space])
async def query_space_list_for_user_group(query_name: str, current_user: User = Depends(deps.get_current_user)):
    return load_space_list_by_name(query_name)


# Topic

@router.get("/topic", tags=["admin"], response_model=Topic)
async def load_topic(topic_id, current_user: User = Depends(deps.get_current_user)):
    # print(topic_id)
    return get_topic_by_id(topic_id)


@router.post("/topic", tags=["admin"], response_model=Topic)
async def create_topic(topic: Topic, current_user: User = Depends(deps.get_current_user)):
    return create_topic_schema(topic)


@router.post("/save/topic", tags=["admin"], response_model=Topic)
async def save_topic(topic: Topic, current_user: User = Depends(deps.get_current_user)):
    if check_fake_id(topic.topicId):
        result = create_topic_schema(topic)
        create_or_update_presto_schema_fields(result)
        return result
    else:
        topic = Topic.parse_obj(topic)
        data = update_topic_schema(topic.topicId, topic)
        ## remove presto shcmea
        create_or_update_presto_schema_fields(data)

        return data


@router.post("/update/topic", tags=["admin"], response_model=Topic)
async def update_topic(topic_id, topic: Topic = Body(...), current_user: User = Depends(deps.get_current_user)):
    topic = Topic.parse_obj(topic)
    data = update_topic_schema(topic_id, topic)
    # remove_presto_schema_by_name(topic.name)
    create_or_update_presto_schema_fields(data)
    return data


@router.post("/topic/name", tags=["admin"], response_model=DataPage)
async def query_topic_list_by_name(query_name: str, pagination: Pagination = Body(...),
                                   current_user: User = Depends(deps.get_current_user)):
    result = query_topic_list_with_pagination(query_name, pagination)
    return result


@router.post("/report/name", tags=["admin"], response_model=DataPage)
async def query_topic_list_by_name(query_name: str, pagination: Pagination = Body(...),
                                   current_user: User = Depends(deps.get_current_user)):
    return query_report_list_with_pagination(query_name, pagination)


@router.get("/topic/all", tags=["admin"], response_model=List[Topic])
async def query_all_topic_list(current_user: User = Depends(deps.get_current_user)):
    result = load_all_topic()
    return result


@router.post("/topic/all/pages", tags=["admin"], response_model=DataPage)
async def query_topic_list_for_pipeline(pagination: Pagination, current_user: User = Depends(deps.get_current_user)):
    result = load_all_topic_list(pagination)
    return result


@router.get("/query/topic/space", tags=["admin"], response_model=List[Topic])
async def query_topic_list_for_space(query_name: str, current_user: User = Depends(deps.get_current_user)):
    return load_topic_list_by_name(query_name)


@router.post("/topic/ids", tags=["admin"], response_model=List[Topic])
async def query_topic_list_by_ids(topic_ids: List[str], current_user: User = Depends(deps.get_current_user)):
    return get_topic_list_by_ids(topic_ids)


# User

@router.post("/user", tags=["admin"], response_model=User)
async def save_user(user: User):
    if user.userId is None or check_fake_id(user.userId):
        return create_user_storage(user)
    else:
        return update_user_storage(user)


@router.post("/user/name", tags=["admin"], response_model=DataPage)
async def query_user_list_by_name(query_name: str, pagination: Pagination = Body(...),
                                  current_user: User = Depends(deps.get_current_user)):
    return query_users_by_name_with_pagination(query_name, pagination)


@router.post("/user/ids", tags=["admin"], response_model=List[User])
async def query_user_list_by_ids(user_ids: List[str], current_user: User = Depends(deps.get_current_user)):
    return get_user_list_by_ids(user_ids)


@router.get("/user", tags=["admin"], response_model=User)
async def load_user(user_id: str, current_user: User = Depends(deps.get_current_user)):
    return get_user(user_id)


@router.get("/query/user/group", tags=["admin"], response_model=List[User])
async def query_user_list_for_user_group(query_name, current_user: User = Depends(deps.get_current_user)):
    return load_user_list_by_name(query_name)


# User Group

@router.post("/user_group", tags=["admin"], response_model=UserGroup)
async def save_user_group(user_group: UserGroup, current_user: User = Depends(deps.get_current_user)):
    if check_fake_id(user_group.userGroupId):
        user_group.userGroupId = None
    if user_group.userGroupId is None or check_fake_id(user_group.userGroupId):
        return create_user_group_storage(user_group)
    else:
        return update_user_group_storage(user_group)


@router.post("/update/user_group", tags=["admin"], response_model=UserGroup)
async def update_user_group(user_group: UserGroup, current_user: User = Depends(deps.get_current_user)):
    return update_user_group_storage(user_group)


@router.get("/query/user_group/space", tags=["admin"], response_model=List[UserGroup])
async def query_group_list_for_space(query_name: str, current_user: User = Depends(deps.get_current_user)):
    return load_group_list_by_name(query_name)


@router.get("/user_group", tags=["admin"], response_model=UserGroup)
async def load_user_group(user_group_id, current_user: User = Depends(deps.get_current_user)):
    return get_user_group(user_group_id)


@router.post("/user_groups/ids", tags=["admin"], response_model=List[UserGroup])
async def query_user_groups_by_ids(user_group_ids: List[str], current_user: User = Depends(deps.get_current_user)):
    return get_user_group_list_by_ids(user_group_ids)


@router.post("/user_group/name", tags=["admin"], response_model=DataPage)
async def query_user_groups_list_by_name(query_name: str, pagination: Pagination = Body(...),
                                         current_user: User = Depends(deps.get_current_user)):
    return query_user_groups_by_name_with_paginate(query_name, pagination)


# pipeline

@router.post("/pipeline", tags=["admin"], response_model=Pipeline)
async def save_pipeline(pipeline: Pipeline, current_user: User = Depends(deps.get_current_user)):
    if pipeline.pipelineId.startswith("f-"):
        return create_pipeline(pipeline)
    else:
        return update_pipeline(pipeline)


@router.get("/pipeline", tags=["admin"], response_model=PipelineFlow)
async def load_pipeline(topic_id, current_user: User = Depends(deps.get_current_user)):
    # pipeline_list_produce = []
    result = load_pipeline_by_topic_id(topic_id)
    pipeline_list_produce = [*result]
    for pipeline in result:
        for stage in pipeline.stages:
            for unit in stage.units:
                for action in unit.do:
                    result = load_pipeline_by_topic_id(action.topicId)
                    pipeline_list_produce = [*pipeline_list_produce, *result]

    return {"topicId": topic_id, "consume": [], "produce": pipeline_list_produce}


@router.get("/pipeline/id", tags=["admin"], response_model=Pipeline)
async def load_pipeline_by_pipeline_id(pipeline_id, current_user: User = Depends(deps.get_current_user)):
    return load_pipeline_by_id(pipeline_id)


@router.get("/pipeline/all", tags=["admin"], response_model=List[Pipeline])
async def load_all_pipelines(current_user: User = Depends(deps.get_current_user)):
    return load_pipeline_list()


@router.get("/pipeline/enabled", tags=["admin"])
async def update_pipeline_enabled(pipeline_id, enabled, current_user: User = Depends(deps.get_current_user)):
    update_pipeline_status(pipeline_id, enabled)


@router.get("/pipeline/rename", tags=["admin"])
async def rename_pipeline(pipeline_id, name, current_user: User = Depends(deps.get_current_user)):
    update_pipeline_name(pipeline_id, name)


@router.post("/pipeline/graphics", tags=["admin"], response_model=PipelinesGraphics)
async def save_pipeline_graph(pipeline_graph: PipelinesGraphics, current_user: User = Depends(deps.get_current_user)):
    user_id = current_user.userId
    result = load_pipeline_graph(user_id)
    if result is not None:
        return update_pipeline_graph(pipeline_graph, user_id)
    else:
        pipeline_graph.userId = user_id
        return create_pipeline_graph(pipeline_graph)


@router.get("/pipeline/graphics/me", tags=["admin"], response_model=PipelinesGraphics)
async def load_pipeline_graph_by_user(current_user: User = Depends(deps.get_current_user)):
    user_id = current_user.userId
    result = load_pipeline_graph(user_id)
    if result is None:
        raise HTTPException(status_code=500, detail="not found pipeline graph")
    else:
        return result


# Report

# TODO report API

# ENUM

@router.post("/enum", tags=["admin"], response_model=Enum)
async def save_enum(enum: Enum):
    return save_enum_to_storage(enum)


@router.post("/enum/name", tags=["admin"], response_model=DataPage)
async def load_enum_list_by_name(query_name, pagination: Pagination = Body(...),
                                 current_user: User = Depends(deps.get_current_user)):
    return query_enum_list_with_pagination(query_name, pagination)


@router.get("/enum", tags=["admin"], response_model=Enum)
async def load_pipeline_by_pipeline_id(enum_id, current_user: User = Depends(deps.get_current_user)):
    return load_enum_by_id(enum_id)
