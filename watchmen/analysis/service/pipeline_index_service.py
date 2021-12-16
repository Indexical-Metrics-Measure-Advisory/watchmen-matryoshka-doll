from datetime import datetime
from typing import List

from model.model.common.parameter import Parameter
from model.model.pipeline.pipeline import Pipeline, UnitAction, Stage, ProcessUnit
from model.model.topic.topic import Topic

from watchmen.analysis.model.pipeline_index import PipelineIndex
from watchmen.analysis.storage import pipeline_index_storage
from watchmen.common.constants import pipeline_constants, parameter_constants
from watchmen.common.constants.parameter_constants import RAW
from watchmen.common.snowflake.snowflake import get_surrogate_key
from watchmen.pipeline.core.case.function.utils import parse_constant_expression, DOT
from watchmen.pipeline.utils.units_func import get_factor, get_factor_by_name
from watchmen.topic.storage.topic_schema_storage import get_topic_by_id

UNDERLINE = "_"

DIRECT_MAPPING = "direct_mapping"
MAPPING_TO = "mapping_to"
LOOP_MAPPING = "loop_mapping"


def __get_pipeline_index_in_dict(topic_id, factor_id, pipeline_id, pipeline_index_dict):
    uni_key = __factor_uni_key(topic_id, factor_id, pipeline_id)
    if uni_key in pipeline_index_dict:
        return pipeline_index_dict[uni_key]
    else:
        pipeline_index = PipelineIndex(topicId=topic_id, factorId=factor_id, pipelineId=pipeline_id)
        pipeline_index.createTime = datetime.now().replace(tzinfo=None).isoformat()
        # pipeline_index.pipelineIndexId = get_surrogate_key()
        pipeline_index_dict[uni_key] = pipeline_index
        return pipeline_index


def __add_mapping_to_pipeline_index(mapping_factor, pipeline_index, pipeline_index_dict):
    topic: Topic = get_topic_by_id(mapping_factor.source.topicId)
    if topic.type != RAW:
        new_pipeline_index = __get_pipeline_index_in_dict(mapping_factor.source.topicId, mapping_factor.source.factorId,
                                                          pipeline_index.pipelineId,
                                                          pipeline_index_dict)
        new_pipeline_index.tenantId = pipeline_index.tenantId
        new_pipeline_index.pipelineName = pipeline_index.pipelineName
        new_pipeline_index.stageId = pipeline_index.stageId
        new_pipeline_index.actionId = pipeline_index.actionId
        new_pipeline_index.stageName = pipeline_index.stageName
        new_pipeline_index.unitName = pipeline_index.unitName
        new_pipeline_index.unitId = pipeline_index.unitId
        new_pipeline_index.refType = MAPPING_TO
        new_pipeline_index.mappingToTopicId = pipeline_index.topicId
        new_pipeline_index.mappingToFactorId = pipeline_index.factorId


def __process_mapping_actions(action: UnitAction, pipeline: Pipeline, pipeline_stage: Stage, pipeline_unit: ProcessUnit,
                              pipeline_index_dict, temporary_context_dict, current_user) -> List[PipelineIndex]:
    for mapping_factor in action.mapping:
        source: Parameter = mapping_factor.source
        pipeline_index = __get_pipeline_index_in_dict(action.topicId, mapping_factor.factorId, pipeline.pipelineId,
                                                      pipeline_index_dict)
        pipeline_index.tenantId = current_user.tenantId
        pipeline_index.pipelineName = pipeline.name
        pipeline_index.stageId = pipeline_stage.stageId
        pipeline_index.actionId = action.actionId
        pipeline_index.stageName = pipeline_stage.name
        pipeline_index.unitName = pipeline_unit.name
        pipeline_index.unitId = pipeline_unit.unitId
        if source.kind == parameter_constants.TOPIC:
            pipeline_index.refType = DIRECT_MAPPING
            pipeline_index.sourceFromTopicId = source.topicId
            pipeline_index.sourceFromFactorId = source.factorId
            __add_mapping_to_pipeline_index(mapping_factor, pipeline_index, pipeline_index_dict)
        elif source.kind == parameter_constants.COMPUTED:
            ##TODO  computed
            pipeline_index.refType = parameter_constants.COMPUTED

        elif source.kind == parameter_constants.CONSTANT:
            parse_constants_parameter(mapping_factor.source.value, pipeline_index, temporary_context_dict)
        # else:
        #     pipeline_index_dict.pop(__factor_uni_key(action.topicId, mapping_factor.factorId, pipeline.pipelineId))
    return pipeline_index_dict


def parse_constants_parameter(constant_value, pipeline_index, temporary_context_dict):
    it = parse_constant_expression(constant_value)
    for item in it:
        if item.startswith('{') and item.endswith('}'):
            var_name = item.lstrip('{').rstrip('}')
            if DOT in var_name:
                variable_name_list = var_name.split(DOT)
                variable_name = variable_name_list[0]
                factor_name = variable_name_list[1]
                if variable_name in temporary_context_dict:
                    topic: Topic = temporary_context_dict.get(variable_name)["topic"]
                    if topic.type == "raw":
                        root_factor_name = temporary_context_dict.get(variable_name)["factor"].name
                        factor = get_factor_by_name(root_factor_name + DOT + factor_name, topic)
                        pipeline_index.refType = LOOP_MAPPING
                        pipeline_index.sourceFromTopicId = topic.topicId
                        pipeline_index.sourceFromFactorId = factor.factorId


def __process_factor_actions(action: UnitAction, pipeline, pipeline_index_dict, temporary_context_dict) -> List[
    PipelineIndex]:
    pass


def __process_read_actions(action: UnitAction, pipeline, temporary_context_dict, current_user):
    if action.type == pipeline_constants.COPY_TO_MEMORY:
        topic = get_topic_by_id(action.source.topicId, current_user)
        factor = get_factor(action.source.factorId, topic)
        temporary_context_dict[action.variableName] = {"topic": topic, "factor": factor}


def __process_by_action_type(action: UnitAction, pipeline: Pipeline, pipeline_stage: Stage, pipeline_unit: ProcessUnit,
                             pipeline_index_dict, temporary_context_dict, current_user) -> List[PipelineIndex]:
    if action.type == pipeline_constants.INSERT_OR_MERGE_ROW \
            or action.type == pipeline_constants.INSERT_ROW \
            or action.type == pipeline_constants.MERGE_ROW:
        return __process_mapping_actions(action, pipeline, pipeline_stage, pipeline_unit, pipeline_index_dict,
                                         temporary_context_dict, current_user)
    elif action.type == pipeline_constants.WRITE_FACTOR:
        return __process_factor_actions(action, pipeline, pipeline_index_dict, temporary_context_dict)
    elif action.type == pipeline_constants.COPY_TO_MEMORY:
        __process_read_actions(action, pipeline, temporary_context_dict, current_user)
    else:
        # __process_read_actions(action)
        pass


async def build_pipeline_index_list(pipeline: Pipeline, pipeline_index_dict, current_user):
    source_topic = get_topic_by_id(pipeline.topicId, current_user)
    pipeline_index_list = []
    temporary_context_dict = {}
    for pipeline_stage in pipeline.stages:
        for pipeline_unit in pipeline_stage.units:
            for action in pipeline_unit.do:
                result_dict = __process_by_action_type(action, pipeline, pipeline_stage, pipeline_unit,
                                                       pipeline_index_dict, temporary_context_dict, current_user)
                if result_dict:
                    for index in result_dict.values():
                        pipeline_index_list.append(index)
    return pipeline_index_list


def __factor_uni_key(topic_id, factor_id, pipeline_id):
    return topic_id + UNDERLINE + factor_id + UNDERLINE + pipeline_id


async def __convert_pipeline_index_dict(pipeline_index_list):
    pipeline_index_dict = {}
    for pipeline_index in pipeline_index_list:
        pipeline_index_dict[__factor_uni_key(pipeline_index.topicId, pipeline_index.factorId,
                                             pipeline_index.pipelineId)] = pipeline_index
    return pipeline_index_dict


async def save_pipeline_index(pipeline: Pipeline, current_user):
    await pipeline_index_storage.delete_pipeline_index_list_by_pipeline_id(pipeline.pipelineId, current_user)
    pipeline_index_list = await build_pipeline_index_list(pipeline, {}, current_user)
    for pipeline_index in pipeline_index_list:
        if pipeline_index.pipelineIndexId is None:
            pipeline_index.pipelineIndexId = get_surrogate_key()
            await pipeline_index_storage.create_pipeline_index(pipeline_index)
        else:
            await pipeline_index_storage.update_pipeline_index(pipeline_index)
