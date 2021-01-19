from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Body

from watchmen.auth.user import User
from watchmen.common import deps
from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.common.utils.data_utils import build_data_pages
from watchmen.console_space.model.console_space import ConsoleSpace, ConsoleSpaceGroup, ConsoleSpaceSubject
from watchmen.console_space.storage.console_group_storage import create_console_group_to_storage, \
    load_console_group_by_id, update_console_group, load_console_group_list_by_ids
from watchmen.console_space.storage.console_space_storage import save_console_space, load_console_space_list_by_user, \
    load_console_space_by_id
from watchmen.console_space.storage.console_subject_storage import create_console_subject_to_storage, \
    load_console_subject_list_by_ids, update_console_subject
from watchmen.report.engine.dataset_engine import load_dataset_by_subject_id
from watchmen.space.service.console import load_topic_list_by_space_id
from watchmen.space.space import Space
from watchmen.space.storage.space_storage import load_space_by_user, get_space_by_id
from watchmen.topic.storage.topic_schema_storage import get_topic_list_by_ids
from watchmen.topic.topic import Topic

router = APIRouter()


# Console API


# TODO console api


class AvailableSpace(Space):
    topics: List[Topic] = []


@router.get("/space/available", tags=["console"], response_model=List[AvailableSpace])
async def load_space_list_by_user(current_user: User = Depends(deps.get_current_user)):
    space_list = load_space_by_user(current_user.groupIds)
    available_space_list = []
    for space in list(space_list):
        space = Space.parse_obj(space)
        available_space = AvailableSpace()
        available_space.spaceId = space.spaceId
        available_space.name = space.name
        available_space.description = space.description
        available_space.topics = get_topic_list_by_ids(space.topicIds)
        available_space_list.append(available_space)
    return available_space_list


@router.get("/space/connect", tags=["console"], response_model=ConsoleSpace)
async def connect_to_space(space_id, name, current_user: User = Depends(deps.get_current_user)):
    # space = get_space_by_id(space_id)
    topic_list = load_topic_list_by_space_id(space_id)

    # TODO load connected space for duplicate check
    console_space = ConsoleSpace()
    console_space.topics = topic_list
    console_space.spaceId = space_id
    console_space.name = name
    console_space.userId = current_user.userId
    console_space.lastVisitTime = datetime.now()
    return save_console_space(console_space)


@router.get("/console_space/connected/me", tags=["console"], response_model=List[ConsoleSpace])
async def load_connected_space(current_user: User = Depends(deps.get_current_user)):
    user_id = current_user.userId
    console_space_list = load_console_space_list_by_user(user_id)
    result = []
    for data in console_space_list:
        console_space = ConsoleSpace.parse_obj(data)
        topic_list = load_topic_list_by_space_id(console_space.spaceId)
        console_space.topics=topic_list

        if console_space.subjectIds is not None:
            subjects = load_console_subject_list_by_ids(console_space.subjectIds)
            # print("subject:",subjects)
            console_space.subjects = subjects

        if console_space.groupIds is not None:
            group_list = load_console_group_list_by_ids(console_space.groupIds)
            for group in group_list:
                console_group = ConsoleSpaceGroup.parse_obj(group)
                subject_list = load_console_subject_list_by_ids(console_group.subjectIds)
                console_group.subjects = subject_list
                console_space.groups.append(console_group)
        result.append(console_space)
    return result


@router.post("/console_space/subject", tags=["console"], response_model=ConsoleSpaceSubject)
async def create_console_subject(connect_id, group_id: Optional[str], subject: ConsoleSpaceSubject = Body(...)):
    console_space = load_console_space_by_id(connect_id)
    subject = create_console_subject_to_storage(subject)
    if group_id is not None and  group_id != "undefined":
        print("group:", group_id)
        group = load_console_group_by_id(group_id)
        group.subjectIds.append(subject.subjectId)
        update_console_group(group)
    else:
        console_space.subjectIds.append(subject.subjectId)
        save_console_space(console_space)

    return subject


@router.post("/console_space/group", tags=["console"], response_model=ConsoleSpaceGroup)
async def create_console_group(connect_id, console_group: ConsoleSpaceGroup = Body(...)):
    console_space = load_console_space_by_id(connect_id)
    console_group = create_console_group_to_storage(console_group)
    console_space.groupIds.append(console_group.groupId)
    save_console_space(console_space)
    return console_group


# @router.post("/space/group", tags=["console"])
# async def save_subject_group(space_id: str, console_space_group: ConsoleSpaceGroup):
#     # load space by space_id
#
#     # save ConsoleSpaceGroup
#
#     # update space_group_ids
#
#     pass

@router.post("/console_space/subject/save", tags=["console"],response_model=ConsoleSpaceSubject)
async def save_console_subject(subject: ConsoleSpaceSubject):
    return update_console_subject(subject)


@router.post("/console_space/subject/dataset", tags=["console"],response_model=DataPage)
async def load_dataset(subject_id,pagination: Pagination = Body(...)):
    data = load_dataset_by_subject_id(subject_id)
    return build_data_pages(pagination, data, 1)