import logging
from typing import List, Any

from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel

from watchmen.auth.service import tenant_service
from watchmen.auth.tenant import Tenant
from watchmen.auth.user import User
from watchmen.collection.model.topic_event import TopicEvent
from watchmen.common import deps
from watchmen.common.constants.parameter_constants import TOPIC, CONSTANT
from watchmen.common.pagination import Pagination
from watchmen.common.parameter import Parameter
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.common.watchmen_model import WatchmenModel
from watchmen.console_space.model.console_space import ConsoleSpaceSubject
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_id
from watchmen.database.mongo.index import delete_topic_collection
from watchmen.database.storage.storage_template import create_raw_pipeline_monitor, clear_metadata, DataPage
from watchmen.monitor.services.pipeline_monitor_service import insert_monitor_topic
from watchmen.pipeline.core.context.pipeline_context import PipelineContext
from watchmen.pipeline.core.dependency.caculate_dependency_new import pipelineExecutionPath
from watchmen.pipeline.core.worker.pipeline_worker import run_pipeline
from watchmen.pipeline.single.stage.unit.utils.units_func import get_factor
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_by_topic_id
from watchmen.raw_data.service.import_raw_data import import_raw_topic_data
from watchmen.report.engine.dataset_engine import get_factor_value_by_subject_and_condition
from watchmen.report.model.filter import Filter
from watchmen.topic.storage.topic_data_storage import find_topic_data_by_id_and_topic_name, \
    update_topic_instance, get_topic_instances_all
from watchmen.topic.storage.topic_schema_storage import get_topic, get_topic_by_id

router = APIRouter()

log = logging.getLogger("app." + __name__)


class TopicInstance(WatchmenModel):
    data: Any = None


@router.get("/health", tags=["common"])
async def health():
    return {"health": True}


## TODO pass user pat when system integration
@router.post("/topic/data", tags=["common"])
async def save_topic_data(topic_event: TopicEvent,current_user: User = Depends(deps.get_current_user)):
    # TODO user check URP
    await import_raw_topic_data(topic_event,current_user)
    # fire_and_forget(task)
    return {"received": True}


@router.get("/topic/data/all", tags=["common"], response_model=List[TopicInstance])
async def load_topic_instance(topic_name, current_user: User = Depends(deps.get_current_user)):
    results = get_topic_instances_all(topic_name)
    instances = []
    for result in results:
        instances.append(TopicInstance(data=result))
    return instances


@router.post("/topic/data/rerun", tags=["common"])  ## TODO  move to pipeline worker
async def rerun_pipeline(topic_name, instance_id, pipeline_id):
    instance = find_topic_data_by_id_and_topic_name(topic_name, instance_id)
    topic = get_topic(topic_name)
    pipeline_list = load_pipeline_by_topic_id(topic.topicId)
    for pipeline in pipeline_list:
        if pipeline.pipelineId == pipeline_id:
            log.info("rerun topic {0} and pipeline {1}".format(topic_name, pipeline.pipelineId))
            pipeline_context = PipelineContext(pipeline, instance)
            run_pipeline(pipeline_context)
    return {"received": True}


@router.post("/topic/data/patch", tags=["common"])
async def patch_topic_instance(topic_name, instance, instance_id):
    result = find_topic_data_by_id_and_topic_name(topic_name, instance_id)
    if result is None:
        raise Exception("topic {0} id {1} not found data ".format(topic_name, instance_id))
    else:
        # TODO audit data
        update_topic_instance(topic_name, instance, instance_id)


@router.post("/topic/data/remove", tags=["common"])
async def remove_topic_collection(collections: List[str], current_user: User = Depends(deps.get_current_user)):
    for collection in collections:
        delete_topic_collection(collection)


class QueryFilter(BaseModel):
    columnName: str = None
    operator: str = None
    value: Any = None


class QueryConditions(BaseModel):
    jointType: str = None
    filters: List[QueryFilter] = []


class QuerySubjectRequest(BaseModel):
    subjectId: str = None
    columnName: str = None
    conditions: QueryConditions = None


def __find_column_by_alias(name, columns):
    for column in columns:
        if column.alias == name:
            return column


def __build_subject_filter(conditions, console_subject: ConsoleSpaceSubject):
    filter_list = []
    for query_filter in conditions.filters:
        column = __find_column_by_alias(query_filter.columnName, console_subject.dataset.columns)
        left = Parameter(kind=TOPIC, type=column.parameter.type, topicId=column.parameter.topicId,
                         factorId=column.parameter.factorId)
        right = Parameter(kind=CONSTANT, value=query_filter.value)
        subject_filter = Filter(left=left, operator=query_filter.operator, right=right)
        filter_list.append(subject_filter)
    subject_conditions = Filter(jointType=conditions.jointType, filters=filter_list)
    return subject_conditions


def __get_factor_name_by_alias(column_name, console_subject):
    column = __find_column_by_alias(column_name, console_subject.dataset.columns)
    factor = get_factor(column.parameter.factorId, get_topic_by_id(column.parameter.topicId))
    return factor.name


@router.post("/subject/query", tags=["common"])
async def get_factor_value_by_topic_name_and_condition(query_subject: QuerySubjectRequest):
    console_subject = load_console_subject_by_id(query_subject.subjectId)
    subject_filter = __build_subject_filter(query_subject.conditions, console_subject)
    factor_name = __get_factor_name_by_alias(query_subject.columnName, console_subject)
    return get_factor_value_by_subject_and_condition(console_subject, factor_name,
                                                     subject_filter)


@router.get("/monitor/pipeline", tags=["common"])
def create_raw_pipeline_monitor_table():
    insert_monitor_topic()
    create_raw_pipeline_monitor()
    return {"created": True}


@router.get("/pipeline/graph/show", tags=["common"])
def show_pipeline_graph(topic_id):
    # pipelines = load_pipeline_by_topic_id(topic_id)
    # buildPipelineGraph(pipelines)
    # buildPipelinesGraph()
    topic = get_topic_by_id(topic_id)
    # pipelineExecutionPath(topic)
    result = pipelineExecutionPath(topic)
    return {"show": result}


# @router.get("/topic/data", tags=["common"])
# def load_topic_instance_data(topic_name,current_user: User = Depends(deps.get_current_user)):
#     return topic_data_list_all(topic_name)


@router.get("/table/metadata/clear", tags=["common"])
def clear_table_metadata():
    clear_metadata()


@router.post("/tenant", tags=["common"], response_model=Tenant)
def save_tenant(tenant: Tenant) -> Tenant:
    if check_fake_id(tenant.tenantId):
        tenant.tenantId = get_surrogate_key()
        return tenant_service.create(tenant)
    else:
        return tenant_service.update(tenant)


@router.post("/tenant/id", tags=["common"], response_model=Tenant)
def load_tenant_by_id(tenant_id: str) -> Tenant:
    return tenant_service.load(tenant_id)


@router.post("/tenant/name", tags=["common"], response_model=DataPage)
def load_tenant_by_name(query_name: str, pagination: Pagination = Body(...),
                        current_user: User = Depends(deps.get_current_user)) -> DataPage:
    return tenant_service.query_by_name(query_name,pagination)
