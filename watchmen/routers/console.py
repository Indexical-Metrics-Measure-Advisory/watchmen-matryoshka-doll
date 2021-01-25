from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Body

from watchmen.auth.user import User
from watchmen.common import deps
from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.common.utils.data_utils import build_data_pages
from watchmen.console_space.model.console_space import ConsoleSpace, ConsoleSpaceGroup, ConsoleSpaceSubject, \
    ConsoleSpaceSubjectChartDataSet
from watchmen.console_space.service.console_space_service import delete_console_subject, \
    delete_console_space_and_sub_data
from watchmen.console_space.storage.console_group_storage import create_console_group_to_storage, \
    load_console_group_by_id, update_console_group, load_console_group_list_by_ids, rename_console_group_by_id
from watchmen.console_space.storage.console_space_storage import save_console_space, load_console_space_list_by_user, \
    load_console_space_by_id, rename_console_space_by_id
from watchmen.console_space.storage.console_subject_storage import create_console_subject_to_storage, \
    load_console_subject_list_by_ids, update_console_subject, rename_console_subject_by_id
from watchmen.dashborad.model.dashborad import ConsoleDashboard
from watchmen.dashborad.storage.dashborad_storage import create_dashboard_to_storage, update_dashboard_to_storage, \
    load_dashboard_by_user_id, delete_dashboard_by_id, rename_dashboard_by_id
from watchmen.monitor.index import is_system_subject, load_system_monitor_chart_data
from watchmen.report.engine.dataset_engine import load_dataset_by_subject_id, load_chart_dataset
from watchmen.space.service.console import load_topic_list_by_space_id
from watchmen.space.space import Space
from watchmen.space.storage.space_storage import load_space_by_user
from watchmen.topic.storage.topic_schema_storage import get_topic_list_by_ids
from watchmen.topic.topic import Topic

router = APIRouter()


# Console API

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


@router.get("/console_space/rename", tags=["console"])
async def rename_console_space(connect_id: str, name: str):
    rename_console_space_by_id(connect_id, name)


@router.get("/console_space/connected/me", tags=["console"], response_model=List[ConsoleSpace])
async def load_connected_space(current_user: User = Depends(deps.get_current_user)):
    user_id = current_user.userId
    console_space_list = load_console_space_list_by_user(user_id)
    result = []
    for data in console_space_list:
        console_space = ConsoleSpace.parse_obj(data)
        topic_list = load_topic_list_by_space_id(console_space.spaceId)
        console_space.topics = topic_list

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


## SUBJECT


@router.post("/console_space/subject", tags=["console"], response_model=ConsoleSpaceSubject)
async def create_console_subject(connect_id, group_id: Optional[str], subject: ConsoleSpaceSubject = Body(...)):
    console_space = load_console_space_by_id(connect_id)
    subject = create_console_subject_to_storage(subject)
    if group_id is not None and group_id != "undefined":
        # print("group:", group_id)
        group = load_console_group_by_id(group_id)
        group.subjectIds.append(subject.subjectId)
        update_console_group(group)
    else:
        console_space.subjectIds.append(subject.subjectId)
        save_console_space(console_space)

    return subject


@router.get("/console_space/delete", tags=["console"])
async def delete_console_space(connect_id, current_user: User = Depends(deps.get_current_user)):
    delete_console_space_and_sub_data(connect_id)


@router.get("/console_space/subject/rename", tags=["console"])
async def rename_console_space_subject(subject_id: str, name: str, current_user: User = Depends(deps.get_current_user)):
    rename_console_subject_by_id(subject_id, name)


@router.get("/console_space/group/rename", tags=["console"])
async def rename_console_group_subject(group_id: str, name: str):
    rename_console_group_by_id(group_id, name)


@router.post("/console_space/group", tags=["console"], response_model=ConsoleSpaceGroup)
async def create_console_group(connect_id, console_group: ConsoleSpaceGroup = Body(...),
                               current_user: User = Depends(deps.get_current_user)):
    console_space = load_console_space_by_id(connect_id)
    console_group = create_console_group_to_storage(console_group)
    console_space.groupIds.append(console_group.groupId)
    save_console_space(console_space)
    return console_group


@router.get("/console_space/subject/delete", tags=["console"])
async def delete_subject(subject_id, current_user: User = Depends(deps.get_current_user)):
    delete_console_subject(subject_id)


@router.post("/console_space/subject/save", tags=["console"], response_model=ConsoleSpaceSubject)
async def save_console_subject(subject: ConsoleSpaceSubject, current_user: User = Depends(deps.get_current_user)):
    return update_console_subject(subject)


@router.post("/console_space/subject/dataset", tags=["console"], response_model=DataPage)
async def load_dataset(subject_id, pagination: Pagination = Body(...),
                       current_user: User = Depends(deps.get_current_user)):
    data, count = load_dataset_by_subject_id(subject_id, pagination)
    return build_data_pages(pagination, data, count)


@router.get("/console_space/dataset/chart", tags=["console"], response_model=ConsoleSpaceSubjectChartDataSet)
async def load_chart(subject_id, chart_id, current_user: User = Depends(deps.get_current_user)):
    if is_system_subject(subject_id):
        return load_system_monitor_chart_data(subject_id, chart_id)
    else:
        result = load_chart_dataset(subject_id, chart_id)
        return ConsoleSpaceSubjectChartDataSet(meta=[], data=result)


## Dashboard

@router.get("/dashboard/create", tags=["console"], response_model=ConsoleDashboard)
async def create_dashboard(name: str, current_user: User = Depends(deps.get_current_user)):
    dashboard = ConsoleDashboard()
    dashboard.name = name
    dashboard.lastVisitTime = datetime.now()
    dashboard.userId = current_user.userId
    return create_dashboard_to_storage(dashboard)


@router.post("/dashboard/save", tags=["console"], response_model=ConsoleDashboard)
async def save_dashboard(dashboard: ConsoleDashboard, current_user: User = Depends(deps.get_current_user)):
    dashboard.userId = current_user.userId
    return update_dashboard_to_storage(dashboard)


@router.get("/dashboard/me", tags=["console"], response_model=List[ConsoleDashboard])
async def load_dashboard(current_user: User = Depends(deps.get_current_user)):
    return load_dashboard_by_user_id(current_user.userId)


@router.get("/dashboard/delete", tags=["console"])
async def delete_dashboard(dashboard_id, current_user: User = Depends(deps.get_current_user)):
    delete_dashboard_by_id(dashboard_id)


@router.get("/dashboard/rename", tags=["console"])
async def delete_dashboard(dashboard_id, name: str, current_user: User = Depends(deps.get_current_user)):
    rename_dashboard_by_id(dashboard_id, name)
