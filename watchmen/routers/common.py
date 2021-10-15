import logging
from typing import List, Any

from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel

from watchmen.auth.service import tenant_service
from watchmen.auth.tenant import Tenant
from watchmen.collection.model.topic_event import TopicEvent
from watchmen.common import deps
from watchmen.common.constants.parameter_constants import TOPIC, CONSTANT
from watchmen.common.model.user import User
from watchmen.common.pagination import Pagination
from watchmen.common.parameter import Parameter
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.common.utils.data_utils import check_fake_id
from watchmen.common.watchmen_model import WatchmenModel
from watchmen.console_space.model.console_space import ConsoleSpaceSubject
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_id
from watchmen.database.datasource.container import data_source_container
from watchmen.database.datasource.data_source import DataSource
from watchmen.database.datasource.storage import data_source_storage
from watchmen.database.mongo.index import delete_topic_collection
from watchmen.database.storage.storage_template import clear_metadata, DataPage
from watchmen.external.model.external_writer import ExternalWriter
from watchmen.external.storage import external_storage
from watchmen.pipeline.core.context.pipeline_context import PipelineContext
from watchmen.pipeline.core.dependency.caculate_dependency_new import pipelineExecutionPath
from watchmen.pipeline.core.worker.pipeline_worker import run_pipeline
from watchmen.pipeline.storage.pipeline_storage import load_pipeline_by_topic_id
from watchmen.pipeline.utils.units_func import get_factor
from watchmen.raw_data.service.import_raw_data import import_raw_topic_data
from watchmen.report.engine.dataset_engine import get_factor_value_by_subject_and_condition
from watchmen.report.model.filter import Filter
from watchmen.topic.storage.topic_data_storage import find_topic_data_by_id_and_topic_name, \
    update_topic_instance, get_topic_instances_all
from watchmen.topic.storage.topic_schema_storage import get_topic, get_topic_by_id, get_topic_by_name
from watchmen.topic.topic import Topic

router = APIRouter()

log = logging.getLogger("app." + __name__)


class TopicInstance(WatchmenModel):
    data: Any = None


@router.get("/health", tags=["common"])
async def health():
    return {"health": True}


@router.post("/topic/data", tags=["common"],deprecated=True)
async def save_topic_data(topic_event: TopicEvent, current_user: User = Depends(deps.get_current_user)):
    # TODO user check URP
    await import_raw_topic_data(topic_event, current_user)
    # fire_and_forget(task)
    return {"received": True}


@router.get("/topic/data/all", tags=["common"], response_model=List[TopicInstance])
async def load_topic_instance(topic_name, current_user: User = Depends(deps.get_current_user)):
    topic: Topic = get_topic_by_name(topic_name, current_user)
    results = get_topic_instances_all(topic)
    instances = []
    for result in results:
        instances.append(TopicInstance(data=result))
    return instances


@router.post("/topic/data/rerun", tags=["common"],deprecated=True)
async def rerun_pipeline(topic_name, instance_id, pipeline_id, current_user: User = Depends(deps.get_current_user)):
    topic = get_topic(topic_name)
    instance = find_topic_data_by_id_and_topic_name(topic, instance_id)
    pipeline_list = load_pipeline_by_topic_id(topic.topicId)
    for pipeline in pipeline_list:
        if pipeline.pipelineId == pipeline_id:
            log.info("rerun topic {0} and pipeline {1}".format(topic_name, pipeline.pipelineId))
            pipeline_context = PipelineContext(pipeline, instance, current_user)
            run_pipeline(pipeline_context)
    return {"received": True}


@router.post("/topic/data/patch", tags=["common"],deprecated=True)
async def patch_topic_instance(topic_name, instance_id,instance= Body(...),current_user: User = Depends(deps.get_current_user)):
    topic = get_topic_by_name(topic_name)
    result = find_topic_data_by_id_and_topic_name(topic, instance_id)
    if result is None:
        raise Exception("topic {0} id {1} not found data ".format(topic_name, instance_id))
    else:
        # TODO audit data

        update_topic_instance(topic, instance, instance_id)


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
    columnNames: List[str] = []
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


def __get_factor_name_by_alias(column_name_list, console_subject):
    factor_name_list = []
    for column_name in column_name_list:
        column = __find_column_by_alias(column_name, console_subject.dataset.columns)
        factor = get_factor(column.parameter.factorId, get_topic_by_id(column.parameter.topicId))
        factor_name_list.append(factor.name)
    return factor_name_list


@router.post("/subject/query", tags=["common"])
async def get_factor_value_by_topic_name_and_condition(query_subject: QuerySubjectRequest,
                                                       current_user: User = Depends(deps.get_current_user)):
    console_subject = load_console_subject_by_id(query_subject.subjectId, current_user)
    subject_filter = __build_subject_filter(query_subject.conditions, console_subject)
    factor_name_list = __get_factor_name_by_alias(query_subject.columnNames, console_subject)
    return get_factor_value_by_subject_and_condition(console_subject, factor_name_list,
                                                     subject_filter)


@router.get("/pipeline/graph/show", tags=["common"])
async def show_pipeline_graph(topic_id):
    topic = get_topic_by_id(topic_id)
    result = pipelineExecutionPath(topic)
    return {"show": result}


@router.get("/table/metadata/clear", tags=["common"])
async def clear_table_metadata():
    clear_metadata()


# TODO current_user
@router.post("/tenant", tags=["common"], response_model=Tenant)
async def save_tenant(tenant: Tenant) -> Tenant:
    if check_fake_id(tenant.tenantId):
        tenant.tenantId = get_surrogate_key()
        return tenant_service.create(tenant)
    else:
        return tenant_service.update(tenant)


@router.post("/tenant/id", tags=["common"], response_model=Tenant)
async def load_tenant_by_id(tenant_id: str) -> Tenant:
    return tenant_service.load(tenant_id)


@router.post("/tenant/name", tags=["common"], response_model=DataPage)
async def load_tenant_by_name(query_name: str, pagination: Pagination = Body(...),
                              current_user: User = Depends(deps.get_current_user)) -> DataPage:
    return tenant_service.query_by_name(query_name, pagination)


@router.get("/datasource/all", tags=["common"], response_model=List[DataSource])
async def load_all_data_sources(current_user: User = Depends(deps.get_current_user)):
    return data_source_storage.load_data_source_list(current_user)


@router.post("/datasource", tags=["common"], response_model=DataSource)
async def save_data_source(data_source: DataSource, current_user: User = Depends(deps.get_current_user)):
    data_source = data_source_storage.save_data_source(data_source)
    data_source_container.init()
    return data_source


@router.get("/datasource/id", tags=["common"], response_model=DataSource)
async def load_data_source(datasource_id: str, current_user: User = Depends(deps.get_current_user)):
    return data_source_storage.load_data_source_by_id(datasource_id, current_user)


@router.post("/datasource/name", tags=["common"], response_model=DataPage)
async def query_data_source_list_by_name(query_name: str, pagination: Pagination = Body(...),
                                         current_user: User = Depends(deps.get_current_user)) -> DataPage:
    return data_source_storage.load_data_source_list_with_pagination(query_name, pagination, current_user)


@router.post("/external_writer", tags=["common"], response_model=ExternalWriter)
async def save_external_writer(external_writer: ExternalWriter, current_user: User = Depends(deps.get_current_user)):
    if check_fake_id(external_writer.writerId):
        external_writer.writerId = get_surrogate_key()
        return external_storage.create(external_writer)
    else:
        return external_storage.update(external_writer)


@router.get("/external_writer/id", tags=["common"], response_model=ExternalWriter)
async def load_external_writer(writer_id: str, current_user: User = Depends(deps.get_current_user)):
    return external_storage.load_external_writer_by_id(writer_id)


@router.post("/external_writer/name", tags=["common"], response_model=DataPage)
async def query_external_writers_by_name(query_name: str, pagination: Pagination = Body(...),
                                         current_user: User = Depends(deps.get_current_user)):
    return external_storage.load_external_writers_with_page(query_name, pagination)


@router.get("/external_writer/all", tags=["common"], response_model=List[ExternalWriter])
async def load_all_external_writers(current_user: User = Depends(deps.get_current_user)):
    return external_storage.load_external_writer_by_tenant_id(current_user.tenantId)
