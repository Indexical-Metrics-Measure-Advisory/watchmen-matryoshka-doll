# IMPORT data
from fastapi import APIRouter

from watchmen.auth.storage.user_group import import_user_group_to_db
from watchmen.auth.user_group import UserGroup
from watchmen.console_space.storage.console_space_storage import import_console_spaces
from watchmen.console_space.storage.console_subject_storage import import_console_subject_to_db
from watchmen.dashborad.storage.dashborad_storage import import_dashboard_to_db
from watchmen.pipeline.storage.pipeline_storage import import_pipeline_to_db
from watchmen.report.storage.report_storage import import_report_to_db
from watchmen.space.storage.space_storage import import_space_to_db
from watchmen.topic.storage.topic_schema_storage import import_topic_to_db

router = APIRouter()

from watchmen.auth.storage.user import import_user_to_db
from watchmen.auth.user import User


### import space

@router.post("/import/admin/user", tags=["import"])
async def import_user(user: User):
    import_user_to_db(user)


### import user group


@router.post("/import/admin/user/group", tags=["import"])
async def import_user_group(group: UserGroup):
    import_user_group_to_db(group)


### import space

@router.post("/import/admin/space", tags=["import"])
async def import_space(space):
    import_space_to_db(space)

## import topic data


@router.post("/import/admin/topic", tags=["import"])
async def import_topic(topic):
    import_topic_to_db(topic)


## import pipeline data

@router.post("/import/admin/pipeline",tags=["import"])
async def import_pipeline(pipeline):
    import_pipeline_to_db(pipeline)


## import connect space
@router.post("/import/console/space",tags=["import"])
async def import_console_space(console_space):
    import_console_spaces(console_space)



## import dataset
@router.post("/import/console/space/subject",tags=["import"])
async  def import_console_subject(subject):
    import_console_subject_to_db(subject)


## import report

@router.post("/import/console/report",tags=["import"])
async def import_console_report(report):
    import_report_to_db(report)


## import dashborad
@router.post("/import/console/dashboard",tags=["import"])
async def import_dashboard(dashboard):
    import_dashboard_to_db(dashboard)


# TODO  import monitor meta
## import monitor meta


