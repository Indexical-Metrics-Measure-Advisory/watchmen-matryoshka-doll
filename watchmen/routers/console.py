from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Body, HTTPException
from pydantic import BaseModel
from starlette import status

from watchmen.auth.storage.user import get_user
from watchmen.common import deps
from watchmen.common.data_page import DataPage
from watchmen.common.model.user import User
from watchmen.common.pagination import Pagination
from watchmen.common.security.index import validate_jwt
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import build_data_pages, check_fake_id, add_tenant_id_to_model
from watchmen.console_space.model.connect_space_graphics import ConnectedSpaceGraphics
from watchmen.console_space.model.console_space import ConsoleSpace, ConsoleSpaceSubject, \
    ConsoleSpaceSubjectChartDataSet, ConnectedSpaceTemplate
from watchmen.console_space.model.favorite import Favorite
from watchmen.console_space.model.last_snapshot import LastSnapshot
from watchmen.console_space.service.console_space_service import delete_console_subject, \
    delete_console_space_and_sub_data, copy_template_to_console_space, load_space_list_by_dashboard
from watchmen.console_space.storage.console_space_storage import save_console_space, load_console_space_list_by_user, \
    load_console_space_by_id, rename_console_space_by_id, create_console_space_graph, update_console_space_graph, \
    load_console_space_graph_by_user_id, load_console_space_graph, load_template_space_list_by_space_id
from watchmen.console_space.storage.console_subject_storage import create_console_subject_to_storage, \
    load_console_subject_list_by_ids, update_console_subject, rename_console_subject_by_id, load_console_subject_by_id, \
    load_console_subject_by_report_id
from watchmen.console_space.storage.favorite_storage import load_favorite, save_favorite
from watchmen.console_space.storage.last_snapshot_storage import load_last_snapshot, save_last_snapshot
from watchmen.dashborad.model.dashborad import ConsoleDashboard
from watchmen.dashborad.storage.dashborad_storage import create_dashboard_to_storage, update_dashboard_to_storage, \
    load_dashboard_by_user_id, delete_dashboard_by_id, rename_dashboard_by_id, load_dashboard_by_id
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


class ShareDashboard(BaseModel):
    dashboard: ConsoleDashboard = None
    reports: List[Report] = []


class SharedSubject(BaseModel):
    subject: ConsoleSpaceSubject = None


@router.get("/space/available", tags=["console"], response_model=List[AvailableSpace])
async def load_space_list_by_user(current_user: User = Depends(deps.get_current_user)):
    space_list = load_space_by_user(current_user.groupIds, current_user)
    available_space_list = []
    for space in list(space_list):
        space = Space.parse_obj(space)
        available_space = AvailableSpace()
        available_space.spaceId = space.spaceId
        available_space.name = space.name
        available_space.description = space.description
        available_space.topicIds = space.topicIds
        available_space_list.append(available_space)
    return available_space_list


@router.get("/console_space/template/list", tags=["console"], response_model=List[ConnectedSpaceTemplate])
async def load_template_space_list(space_id: str, current_user: User = Depends(deps.get_current_user)):
    results: List[ConsoleSpace] = load_template_space_list_by_space_id(space_id)
    template_list = []
    for console_space in results:
        print("user", console_space.userId)
        user = get_user(console_space.userId)
        template_list.append(
            ConnectedSpaceTemplate(connectId=console_space.connectId, name=console_space.name, createBy=user.name))
    return template_list


@router.get("/space/connect", tags=["console"], response_model=ConsoleSpace)
async def connect_to_space(space_id, name, template_ids=None, current_user: User = Depends(deps.get_current_user)):
    console_space = ConsoleSpace()
    console_space = add_tenant_id_to_model(console_space, current_user)
    console_space.topics = load_topic_list_by_space_id(space_id, current_user)
    console_space.spaceId = space_id
    console_space.name = name
    console_space.userId = current_user.userId
    console_space.lastVisitTime = datetime.now().replace(tzinfo=None)
    if template_ids:
        console_space = copy_template_to_console_space(template_ids, console_space, current_user)
    console_space = save_console_space(console_space)
    return console_space


@router.post("/console_space/save", tags=["console"], response_model=ConsoleSpace)
async def update_console_space(console_space: ConsoleSpace, current_user: User = Depends(deps.get_current_user)):
    console_space = add_tenant_id_to_model(console_space, current_user)
    console_space.userId = current_user.userId
    return save_console_space(console_space)


@router.get("/console_space/rename", tags=["console"])
async def rename_console_space(connect_id: str, name: str, current_user: User = Depends(deps.get_current_user)):
    rename_console_space_by_id(connect_id, name)


@router.get("/console_space/connected/me", tags=["console"], response_model=List[ConsoleSpace])
async def load_connected_space(current_user: User = Depends(deps.get_current_user)):
    user_id = current_user.userId
    console_space_list = load_console_space_list_by_user(user_id, current_user)
    result = []
    for console_space in console_space_list:
        topic_list = load_topic_list_by_space_id(console_space.spaceId, current_user)
        console_space.topics = topic_list
        if console_space.subjectIds is not None:
            subjects = load_console_subject_list_by_ids(console_space.subjectIds, current_user)
            for subject in subjects:
                subject.reports = load_reports_by_ids(subject.reportIds, current_user)
            console_space.subjects = subjects
        result.append(console_space)
    return result


## SUBJECT

@router.post("/console_space/subject", tags=["console"], response_model=ConsoleSpaceSubject)
async def create_console_subject(connect_id, subject: ConsoleSpaceSubject = Body(...),
                                 current_user: User = Depends(deps.get_current_user)):
    subject = add_tenant_id_to_model(subject, current_user)
    if check_fake_id(subject.subjectId):
        subject.subjectId = None
        console_space = load_console_space_by_id(connect_id, current_user)
        for report in subject.reports:
            report.reportId = get_surrogate_key()
            subject.reportIds.append(report.reportId)

        subject = create_console_subject_to_storage(subject)
        console_space.subjectIds.append(subject.subjectId)
        save_console_space(console_space)
        return subject
    else:
        raise Exception("id is not fake ID")


@router.get("/console_space/delete", tags=["console"])
async def delete_console_space(connect_id, current_user: User = Depends(deps.get_current_user)):
    delete_console_space_and_sub_data(connect_id, current_user)


@router.get("/console_space/subject/rename", tags=["console"])
async def rename_console_space_subject(subject_id: str, name: str, current_user: User = Depends(deps.get_current_user)):
    rename_console_subject_by_id(subject_id, name)


@router.get("/console_space/subject/delete", tags=["console"])
async def delete_subject(subject_id, current_user: User = Depends(deps.get_current_user)):
    delete_console_subject(subject_id, current_user)


@router.post("/console_space/subject/save", tags=["console"], response_model=ConsoleSpaceSubject)
async def save_console_subject(subject: ConsoleSpaceSubject, current_user: User = Depends(deps.get_current_user)):
    subject = add_tenant_id_to_model(subject, current_user)
    for report in subject.reports:
        subject.reportIds.append(report.reportId)
    subject.reports = []
    return update_console_subject(subject)


@router.post("/console_space/subject/dataset", tags=["console"], response_model=DataPage)
async def load_dataset(subject_id, pagination: Pagination = Body(...),
                       current_user: User = Depends(deps.get_current_user)):
    data, count = await load_dataset_by_subject_id(subject_id, pagination, current_user)
    return build_data_pages(pagination, data, count)


@router.post("/console_space/graphics", tags=["console"], response_model=ConnectedSpaceGraphics)
async def save_console_space_graph(console_space_graph: ConnectedSpaceGraphics,
                                   current_user: User = Depends(deps.get_current_user)):
    console_space_graph = add_tenant_id_to_model(console_space_graph, current_user)
    old_console_space_graph = load_console_space_graph(console_space_graph.connectId, current_user)
    console_space_graph.userId = current_user.userId
    if old_console_space_graph is None:
        create_console_space_graph(console_space_graph)
    else:
        update_console_space_graph(console_space_graph)
    return console_space_graph


@router.get("/console_space/graphics/me", tags=["console"], response_model=List[ConnectedSpaceGraphics])
async def load_my_console_space_graph(current_user: User = Depends(deps.get_current_user)):
    return load_console_space_graph_by_user_id(current_user.userId, current_user)


@router.post("/console_space/subject/report/save", tags=["console"], response_model=Report)
async def save_report(subject_id: str, report: Report, current_user: User = Depends(deps.get_current_user)):
    report = add_tenant_id_to_model(report, current_user)
    report.reportId = get_surrogate_key()
    # report.subjectId = subject_id
    new_report = create_report(report)
    subject = load_console_subject_by_id(subject_id, current_user)
    subject.reportIds.append(report.reportId)
    update_console_subject(subject)
    return new_report


@router.post("/console_space/subject/report/update", tags=["console"], response_model=Report)
async def update_report(report: Report, current_user: User = Depends(deps.get_current_user)):
    report = add_tenant_id_to_model(report, current_user)
    save_subject_report(report)
    return report


@router.get("/console_space/subject/report/delete", tags=["console"])
async def delete_report(report_id, current_user: User = Depends(deps.get_current_user)):
    subject = load_console_subject_by_report_id(report_id, current_user)
    subject.reportIds.remove(report_id)
    update_console_subject(subject)
    delete_report_by_id(report_id)


@router.get("/console_space/dataset/chart", tags=["console"], response_model=ConsoleSpaceSubjectChartDataSet)
async def load_chart(report_id, current_user: User = Depends(deps.get_current_user)):
    result = await load_chart_dataset(report_id, current_user)
    return ConsoleSpaceSubjectChartDataSet(meta=[], data=result)


@router.post("/console_space/dataset/chart/temporary", tags=["console"], response_model=ConsoleSpaceSubjectChartDataSet)
async def load_temporary_chart(report: Report, current_user: User = Depends(deps.get_current_user)):
    result = load_chart_dataset_temp(report, current_user)
    return ConsoleSpaceSubjectChartDataSet(meta=[], data=result)


## Dashboard

@router.get("/dashboard/create", tags=["console"], response_model=ConsoleDashboard)
async def create_dashboard(name: str, current_user: User = Depends(deps.get_current_user)):
    dashboard = ConsoleDashboard()
    dashboard = add_tenant_id_to_model(dashboard, current_user)
    dashboard.name = name
    dashboard.userId = current_user.userId
    return create_dashboard_to_storage(dashboard)


@router.post("/dashboard/save", tags=["console"], response_model=ConsoleDashboard)
async def save_dashboard(dashboard: ConsoleDashboard, current_user: User = Depends(deps.get_current_user)):
    dashboard.userId = current_user.userId
    dashboard = add_tenant_id_to_model(dashboard, current_user)
    return update_dashboard_to_storage(dashboard)


@router.get("/dashboard/me", tags=["console"], response_model=List[ConsoleDashboard])
async def load_dashboard(current_user: User = Depends(deps.get_current_user)):
    return load_dashboard_by_user_id(current_user.userId, current_user)


@router.get("/dashboard/delete", tags=["console"])
async def delete_dashboard(dashboard_id, current_user: User = Depends(deps.get_current_user)):
    delete_dashboard_by_id(dashboard_id)


@router.get("/dashboard/rename", tags=["console"])
async def rename_dashboard(dashboard_id, name: str, current_user: User = Depends(deps.get_current_user)):
    rename_dashboard_by_id(dashboard_id, name)


##Share
@router.get("/share/dashboard", tags=["share"], response_model=ShareDashboard)
async def share_dashboard(dashboard_id: str, token: str):
    security_payload = validate_jwt(token)
    user: User = get_user(security_payload["sub"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    dashboard = load_dashboard_by_id(dashboard_id, user)
    return load_space_list_by_dashboard(dashboard)


@router.get("/share/subject", tags=["share"], response_model=ConsoleSpaceSubject)
async def share_subject(subject_id: str, token: str):
    security_payload = validate_jwt(token)
    user = get_user(security_payload["sub"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    subject = load_console_subject_by_id(subject_id, user)
    return {"subject": subject}


## FAVORITE

@router.get('/favorites/me', tags=["console"], response_model=Favorite)
async def load_favorites_by_user(current_user: User = Depends(deps.get_current_user)):
    result = load_favorite(current_user.userId, current_user)
    if result is None:
        return Favorite()
    else:
        return result


@router.post('/favorites/save', tags=["console"], response_model=Favorite)
async def save_favorite_with_user(favorite: Favorite, current_user: User = Depends(deps.get_current_user)):
    favorite.userId = current_user.userId
    favorite = add_tenant_id_to_model(favorite, current_user)
    save_favorite(favorite, current_user)
    return favorite


## LastSnapshot
@router.get('/last_snapshot/me', tags=["console"], response_model=LastSnapshot)
async def load_last_snapshot_by_user(current_user: User = Depends(deps.get_current_user)):
    result = load_last_snapshot(current_user.userId, current_user)
    if result is None:
        return LastSnapshot()
    else:
        return result


@router.post('/last_snapshot/save', tags=["console"], response_model=LastSnapshot)
async def save_last_snapshot_with_user(last_snapshot: LastSnapshot,
                                       current_user: User = Depends(deps.get_current_user)):
    last_snapshot.userId = current_user.userId
    last_snapshot = add_tenant_id_to_model(last_snapshot, current_user)
    save_last_snapshot(last_snapshot, current_user)
    return last_snapshot
