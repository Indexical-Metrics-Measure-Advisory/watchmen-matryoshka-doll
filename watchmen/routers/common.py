import logging
from typing import List, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from watchmen.auth.user import User
from watchmen.collection.model.topic_event import TopicEvent
from watchmen.common import deps
from watchmen.common.constants.parameter_constants import TOPIC, CONSTANT
from watchmen.common.mongo.index import delete_topic_collection
from watchmen.common.mongo_model import MongoModel
from watchmen.common.parameter import Parameter
from watchmen.console_space.model.console_space import ConsoleSpaceSubject
from watchmen.console_space.storage.console_subject_storage import load_console_subject_by_id
from watchmen.pipeline.single.pipeline_service import run_pipeline
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


class TopicInstance(MongoModel):
    data: Any = None


@router.get("/health", tags=["common"])
async def health():
    return {"health": True}


@router.post("/topic/data", tags=["common"])
async def save_topic_data(topic_event: TopicEvent):
    # TODO user check URP

    await import_raw_topic_data(topic_event)
    return {"received": True}


@router.get("/topic/data/all", tags=["common"], response_model=List[TopicInstance])
async def load_topic_instance(topic_name, current_user: User = Depends(deps.get_current_user)):
    results = get_topic_instances_all(topic_name)
    instances = []
    for result in results:
        instances.append(TopicInstance(data=result))
    return instances


@router.post("/topic/data/rerun", tags=["common"])
async def rerun_pipeline(topic_name, instance_id, pipeline_id):
    instance = find_topic_data_by_id_and_topic_name(topic_name, instance_id)
    topic = get_topic(topic_name)
    pipeline_list = load_pipeline_by_topic_id(topic.topicId)
    for pipeline in pipeline_list:
        if pipeline.pipelineId == pipeline_id:
            log.info("rerun topic {0} and pipeline {1}".format(topic_name, pipeline.pipelineId))
            run_pipeline(pipeline, instance)
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


def __find_column_by_alias(name,columns):
    for column in columns:
        if column.alias == name:
            return column


def __build_subject_filter(conditions,console_subject:ConsoleSpaceSubject):
    filter_list = []
    for query_filter in conditions.filters:
        column = __find_column_by_alias(query_filter.columnName,console_subject.dataset.columns)
        left = Parameter(kind=TOPIC,type=column.parameter.type,topicId=column.parameter.topicId,factorId=column.parameter.factorId)
        right = Parameter(kind=CONSTANT,value=query_filter.value)
        subject_filter = Filter(left=left,operator=query_filter.operator,right=right)
        filter_list.append(subject_filter)
    subject_conditions = Filter(jointType=conditions.jointType,filters=filter_list)
    return subject_conditions


def __get_factor_name_by_alias(column_name,console_subject):
    column = __find_column_by_alias(column_name, console_subject.dataset.columns)
    factor = get_factor(column.parameter.factorId,get_topic_by_id(column.parameter.topicId))
    return factor.name


@router.post("/subject/query", tags=["common"])
async def get_factor_value_by_topic_name_and_condition(query_subject: QuerySubjectRequest):
    console_subject = load_console_subject_by_id(query_subject.subjectId)
    subject_filter = __build_subject_filter(query_subject.conditions,console_subject)
    factor_name = __get_factor_name_by_alias(query_subject.columnName,console_subject)
    return get_factor_value_by_subject_and_condition(console_subject, factor_name,
                                                     subject_filter)
