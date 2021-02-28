from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Body

from watchmen.auth.user import User
from watchmen.common import deps
from watchmen.common.data_page import DataPage
from watchmen.common.pagination import Pagination
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import build_data_pages, check_fake_id
from watchmen.console_space.model.connect_space_graphics import ConnectedSpaceGraphics
from watchmen.console_space.model.console_space import ConsoleSpace, ConsoleSpaceGroup, ConsoleSpaceSubject, \
    ConsoleSpaceSubjectChartDataSet
from watchmen.console_space.service.console_space_service import delete_console_subject, \
    delete_console_space_and_sub_data
from watchmen.console_space.storage.console_group_storage import create_console_group_to_storage, \
    rename_console_group_by_id
from watchmen.console_space.storage.console_space_storage import save_console_space, load_console_space_list_by_user, \
    load_console_space_by_id, rename_console_space_by_id, create_console_space_graph, update_console_space_graph, \
    load_console_space_graph_by_user_id
from watchmen.console_space.storage.console_subject_storage import create_console_subject_to_storage, \
    load_console_subject_list_by_ids, update_console_subject, rename_console_subject_by_id, load_console_subject_by_id, \
    load_console_subject_by_report_id
from watchmen.dashborad.model.dashborad import ConsoleDashboard
from watchmen.dashborad.storage.dashborad_storage import create_dashboard_to_storage, update_dashboard_to_storage, \
    load_dashboard_by_user_id, delete_dashboard_by_id, rename_dashboard_by_id
from watchmen.report.engine.dataset_engine import load_dataset_by_subject_id, load_chart_dataset, \
    load_chart_dataset_temp
from watchmen.report.model.report import Report
from watchmen.report.storage.report_storage import create_report, save_subject_report, \
    load_reports_by_ids, delete_report_by_id
from watchmen.space.service.console import load_topic_list_by_space_id
from watchmen.space.space import Space
from watchmen.space.storage.space_storage import load_space_by_user
from watchmen.topic.topic import Topic
from watchmen.topic.topic_relationship import TopicRelationship

router = APIRouter()


# Console API

class AvailableSpace(Space):
    topics: List[Topic] = []
    topicRelations: List[TopicRelationship] = []


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
        available_space.topicIds = space.topicIds
        # available_space.topicRelations =load_relationships_by_topic_ids(space.topicIds)
        available_space_list.append(available_space)
    return available_space_list


@router.get("/space/connect", tags=["console"], response_model=ConsoleSpace)
async def connect_to_space(space_id, name, current_user: User = Depends(deps.get_current_user)):
    # space = get_space_by_id(space_id)
    topic_list = load_topic_list_by_space_id(space_id)
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
        # topic_ids = list(map(lambda x: x["topicId"], topic_list))
        # source_relation = load_relationships_by_topic_ids(topic_ids)
        # target_relation = load_relationships_by_topic_ids_target(topic_ids)
        # console_space.topicRelations = [*source_relation, *target_relation]

        if console_space.subjectIds is not None:
            subjects = load_console_subject_list_by_ids(console_space.subjectIds)
            for subject in subjects:
                subject["reports"] = load_reports_by_ids(subject["reportIds"])
            console_space.subjects = subjects
        result.append(console_space)
    return result


## SUBJECT


@router.post("/console_space/subject", tags=["console"], response_model=ConsoleSpaceSubject)
async def create_console_subject(connect_id, subject: ConsoleSpaceSubject = Body(...)):
    if check_fake_id(subject.subjectId):
        subject.subjectId = None
        console_space = load_console_space_by_id(connect_id)

        for report in subject.reports:
            report.reportId = get_surrogate_key()
            subject.reportIds.append(report.reportId)

        subject = create_console_subject_to_storage(subject)
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
    subject.reports = []
    return update_console_subject(subject)


@router.post("/console_space/subject/dataset", tags=["console"], response_model=DataPage)
async def load_dataset(subject_id, pagination: Pagination = Body(...),
                       current_user: User = Depends(deps.get_current_user)):
    data, count = load_dataset_by_subject_id(subject_id, pagination)
    return build_data_pages(pagination, data, count)


@router.post("/console_space/graphics", tags=["console"], response_model=ConnectedSpaceGraphics)
async def save_console_space_graph(console_space_graph: ConnectedSpaceGraphics,
                                   current_user: User = Depends(deps.get_current_user)):

    old_console_space_graph = load_console_space_graph_by_user_id(current_user.userId)
    console_space_graph.userId = current_user.userId

    if old_console_space_graph is None:
        create_console_space_graph(console_space_graph)
    else:
        update_console_space_graph(console_space_graph)
    return console_space_graph


@router.get("/console_space/graphics/me", tags=["console"], response_model=List[ConnectedSpaceGraphics])
async def load_my_console_space_graph(current_user: User = Depends(deps.get_current_user)):
    return load_console_space_graph_by_user_id(current_user.userId)


@router.post("/console_space/subject/report/save", tags=["console"], response_model=Report)
async def save_report(subject_id: str, report: Report, current_user: User = Depends(deps.get_current_user)):
    report.reportId = get_surrogate_key()
    report.subjectId = subject_id
    new_report = create_report(report)
    subject = load_console_subject_by_id(subject_id)
    subject.reportIds.append(report.reportId)
    update_console_subject(subject)
    return new_report


@router.post("/console_space/subject/report/update", tags=["console"], response_model=Report)
async def update_report(report: Report, current_user: User = Depends(deps.get_current_user)):
    save_subject_report(report)
    return report


@router.get("/console_space/subject/report/delete", tags=["console"])
async def delete_report(report_id):
    subject = load_console_subject_by_report_id(report_id)
    subject.reportIds.remove(report_id)
    update_console_subject(subject)
    delete_report_by_id(report_id)


@router.get("/console_space/dataset/chart", tags=["console"], response_model=ConsoleSpaceSubjectChartDataSet)
async def load_chart(report_id, current_user: User = Depends(deps.get_current_user)):
    result = load_chart_dataset(report_id)
    return ConsoleSpaceSubjectChartDataSet(meta=[], data=result)


@router.post("/console_space/dataset/chart/temporary", tags=["console"], response_model=ConsoleSpaceSubjectChartDataSet)
async def load_temporary_chart(report: Report):
    result = load_chart_dataset_temp(report)
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
async def rename_dashboard(dashboard_id, name: str, current_user: User = Depends(deps.get_current_user)):
    rename_dashboard_by_id(dashboard_id, name)
