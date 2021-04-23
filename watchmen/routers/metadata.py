# IMPORT data
from fastapi import APIRouter

from watchmen.auth.storage.user_group import import_user_group_to_db, get_user_group, update_user_group_storage
from watchmen.auth.user_group import UserGroup
from watchmen.console_space.model.console_space import ConsoleSpace, ConsoleSpaceSubject
from watchmen.console_space.storage.console_space_storage import import_console_spaces, load_console_space_by_id, \
    update_console_space
from watchmen.console_space.storage.console_subject_storage import import_console_subject_to_db, \
    load_console_subject_by_id, update_console_subject
from watchmen.dashborad.model.dashborad import ConsoleDashboard
from watchmen.dashborad.storage.dashborad_storage import import_dashboard_to_db, load_dashboard_by_id, \
    update_dashboard_to_storage
from watchmen.pipeline.model.pipeline import Pipeline
from watchmen.pipeline.storage.pipeline_storage import import_pipeline_to_db, load_pipeline_by_id, update_pipeline
from watchmen.report.model.report import Report
from watchmen.report.storage.report_storage import import_report_to_db, load_report_by_id, save_subject_report
from watchmen.space.service.admin import update_space_by_id
from watchmen.space.space import Space
from watchmen.space.storage.space_storage import import_space_to_db, get_space_by_id
from watchmen.topic.service.topic_service import update_topic_schema, create_topic_schema
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id
from watchmen.topic.topic import Topic

router = APIRouter()

from watchmen.auth.storage.user import import_user_to_db, get_user, update_user_storage
from watchmen.auth.user import User


### import space

@router.post("/import/admin/user", tags=["import"])
async def import_user(user: User):
    result = get_user(user.userId)
    if result is None:
        import_user_to_db(user)
    else:
        update_user_storage(user)


### import user group


@router.post("/import/admin/user/group", tags=["import"])
async def import_user_group(group: UserGroup):
    result = get_user_group(group.userGroupId)
    if result is None:
        import_user_group_to_db(group)
    else:
        update_user_group_storage(group)


### import space

@router.post("/import/admin/space", tags=["import"])
async def import_space(space: Space):
    result = get_space_by_id(space.spaceId)
    if result is None:
        import_space_to_db(space)
    else:
        update_space_by_id(space.spaceId, space)


## import topic data
@router.post("/import/admin/topic", tags=["import"])
async def import_topic(topic: Topic):
    result = get_topic_by_id(topic.topicId)
    if result is None:
        # import_topic_to_db(topic)
        create_topic_schema(topic)
    else:
        update_topic_schema(topic.topicId, topic)


## import pipeline data

@router.post("/import/admin/pipeline", tags=["import"])
async def import_pipeline(pipeline: Pipeline):
    result = load_pipeline_by_id(pipeline.pipelineId)
    if result is None:
        import_pipeline_to_db(pipeline)
    else:
        update_pipeline(pipeline)


## import connect space
@router.post("/import/console/space", tags=["import"])
async def import_console_space(console_space: ConsoleSpace):
    result = load_console_space_by_id(console_space.connectId)
    if result is None:
        import_console_spaces(console_space)
    else:
        update_console_space(console_space)


## import dataset
@router.post("/import/console/space/subject", tags=["import"])
async def import_console_subject(subject: ConsoleSpaceSubject):
    result = load_console_subject_by_id(subject.subjectId)
    if result is None:
        import_console_subject_to_db(subject)
    else:
        update_console_subject(subject)


## import report

@router.post("/import/console/report", tags=["import"])
async def import_console_report(report: Report):
    result = load_report_by_id(report.reportId)
    if result is None:
        import_report_to_db(report)
    else:
        save_subject_report(report)


## import dashborad
@router.post("/import/console/dashboard", tags=["import"])
async def import_dashboard(dashboard: ConsoleDashboard):
    result = load_dashboard_by_id(dashboard.dashboardId)
    if result is None:
        import_dashboard_to_db(dashboard)
    else:
        update_dashboard_to_storage(dashboard)

### search

# async def search_data_import()
